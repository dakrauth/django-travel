//------------------------------------------------------------------------------
// Sample entity object
//------------------------------------------------------------------------------
// entity = {
//     "flag_svg": "img/wh-32.png",
//     "code": "3",
//     "name": "Aachen Cathedral",
//     "locality": "State of North Rhine-Westphalia (Nordrhein-Westfalen)",
//     "country_flag_svg": "img/flags/co/de/de-32.png",
//     "country_code": "DE",
//     "country_name": "Germany",
//     "type_abbr": "wh",
//     "id": 11942
// }
//}
//------------------------------------------------------------------------------

;const Travelogue = (function(root) {

    const MISSING_FLAG = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-geo-alt-fill" viewBox="0 0 16 16"><path d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10zm0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"/></svg>'
    const DATE_FORMAT  = 'YYYY-MM-DD';
    const TYPE_MAPPING = {
        'cn': 'Continent', 'co': 'Country', 'wh': 'World Heritage',
        'st': 'State',     'ap': 'Airport',  'np': 'National Park',
        'lm': 'Landmark',  'ct': 'City'
    };

    const renderTemplate = function(templateId, data) {
        const template = document.getElementById(templateId);
        const node = template.content.cloneNode(true);
        for(const [key, value] of Object.entries(data)) {
            const el = node.querySelector(`.${key}`)
            if(el) {
                if(typeof value === 'string') {
                    el.textContent = value;
                }
            }
        }
        return node;
    };

    const createLogRow = log => {
        let extras = [];
        const e = log.entity;
        const firstArrival = e.logs[e.logs.length-1].arrival;
        const dateFormat  = 'ddd MMM Do YYYY h:ssa';
        const stars = rating => '★★★★★'.substr(rating - 1);

        e.locality && extras.push(e.locality);
        e.country_name && extras.push(e.country_name);

        const node = renderTemplate('log-row', {
            'log-category': TYPE_MAPPING[e.type_abbr],
            'log-country': extras.join(', '),
            'log-count': e.logs.length.toString(),
            'log-rating': stars(log.rating),
            'log-recent-visit': log.arrival.format(dateFormat),
            'log-country-flag-emoji': e.country_flag_emoji,
            'log-first-visit': firstArrival.format(dateFormat)
        });

        const countryFlag = node.querySelector('.log-country-flag');
        if(countryFlag) {
            countryFlag.src = e.country_flag_svg;
        }
        else {
            countryFlag.remove();
        }

        const logName = node.querySelector('.log-name');
        logName.href = e.url;
        logName.textContent = e.name;

        const logImage = node.querySelector('.log-image');
        logImage.src = e.flag_svg || MISSING_FLAG;

        const tr = node.querySelector('tr');
        tr.dataset.id = e.id;
        tr.dataset.name = e.name;
        tr.dataset.arrival = log.arrival.valueOf();
        tr.dataset.first = firstArrival.valueOf();
        tr.dataset.count = e.logs.length;
        tr.dataset.rating = log.rating;

        tr.className = e.type_abbr + ' co-' + (
            e.country_code ?
            e.country_code :
            (e.type_abbr == 'co' ? e.code : '')
        );
        return node;
    };

    const showLogs = travelLogs => {
        console.time('showLogs');
        const count = travelLogs.logs.length;
        let parent = document.getElementById('history');
        let el = parent.querySelector('tbody');

        document.getElementById('id_count').textContent = (count + ' entr' + (count > 1 ? 'ies' : 'y'));
        el.parentNode.removeChild(el);
        el = document.createElement('tbody');

        console.time('createLogRows');
        for(const log of travelLogs.logs) {
            if(log.isActive) {
                el.appendChild(createLogRow(log));
            }
        }
        console.timeEnd('createLogRows');

        parent.appendChild(el);
        travelLogs.summary.render();
        console.timeEnd('showLogs');
    };

    const getOrdering = el => {
        const ordering = {'column': el.dataset.column, 'order': el.dataset.order};
        const current = el.parentElement.querySelector('.current');
        if(el === current) {
            ordering.order = (ordering.order === 'desc') ? 'asc' : 'desc';
            el.dataset.order = ordering.order;
        }
        else {
            current.className = '';
            el.className = 'current';
        }
        return ordering;
    };

    class Summary {
        constructor() {
            for(const key of Object.keys(TYPE_MAPPING)) {
                this[key] = {};
            }
        }
        add(e) {
            const kind = this[e.type_abbr];
            kind[e.id] = 1 + (kind[e.id] || 0);
        }
        render() {
            const el = document.getElementById('summary');
            while(el.lastChild) {
              el.removeChild(el.lastChild);
            }

            const strong = document.createElement('strong');
            strong.textContent = 'Summary: ';
            el.appendChild(strong);
            for(const key of Object.keys(this)) {
                const items = Object.keys(this[key]).length;
                if(items) {
                    const span = document.createElement('span');
                    span.className = 'label label-info';
                    span.textContent = TYPE_MAPPING[key] + ': ' + items
                    el.appendChild(span);
                }
            }
        }
    }

    const sorters = {
        type: (a, b) => (b.entity.type_abbr > a.entity.type_abbr) ? 1: -1,
        name: (a, b) => (b.entity.name > a.name) ? 1 : -1,
        recent_visit: (a, b) => b.arrival.valueOf() - a.arrival.valueOf(),
        first_visit: (a, b) => {
            const aLogs = a.entity.logs;
            const bLogs = b.entity.logs;
            return (
                bLogs[bLogs.length - 1].arrival.valueOf()
              - aLogs[aLogs.length - 1].arrival.valueOf()
            );
        },
        num_visits: (a, b) => b.entity.logs.length - a.entity.logs.length,
        rating: (a, b) => a.rating - b.rating
    };

    class LogEntry{
        constructor(e) {
            Object.assign(this, e);
            this.logs = [];
        }
    }

    class TravelLogs {
        constructor(logs, summary) {
            this.logs = logs;
            this.summary = summary;
        }
        sortLogs(column, order) {
            console.log('ordering', column, order);
            this.logs.sort(sorters[column]);
            if(order === 'desc') {
                this.logs.reverse()
            }
        }
        filter(bits) {
            console.log('filter bits', bits);
            this.summary = new Summary();
            for(const log of this.logs) {
                const e = log.entity;
                let good = true;
                if(bits.type) {
                    good = (e.type_abbr === bits.type);
                }

                if(good && bits.co) {
                    good = (
                        e.country_code === bits.co ||
                        (e.type_abbr === 'co' && e.code === bits.co)
                    );
                }

                if(good && bits.limit) {
                    if(e.logs.length === 1) {
                        good = true;
                    }
                    else if(bits.limit === 'recent') {
                        good = e.logs[0].id === log.id;
                    }
                    else {
                        good = e.logs[e.logs.length - 1].id == log.id;
                    }
                }

                if(good && bits.timeframe && bits.date) {
                    switch(bits.timeframe) {
                        case '+':
                            good = log.arrival.isAfter(bits.date);
                            break;
                        case '-':
                            good = log.arrival.isBefore(bits.date);
                            break;
                        case '=':
                            good = (log.arrival.year() === bits.date);
                            break;
                        default:
                            good = false;
                    }
                }

                if(good) {
                    this.summary.add(e);
                }

                log.isActive = good;
            }

            return this;
        }
    }

    const initOrderingByColumns = controller => {
        for(const e of document.querySelectorAll('#history thead th[data-column]')) {
            e.addEventListener('click', evt => {
                const ordering = getOrdering(e);
                if(ordering.order === 'asc') {
                    HashBits.fromFilters().update();
                }
                controller.sortLogs(ordering.column, ordering.order);
            }, false)
        };
    };

    const createCountryOptions = countries => {
        const cos = document.getElementById('id_co');
        for(const key of Object.keys(countries).sort()) {
            const el = document.createElement('option');
            el.textContent = countries[key];
            el.value = key;
            cos.appendChild(el);
        }
    };

    const createYearsOption = keys => {
        const sel = document.createElement('select');
        sel.className = 'filter_ctrl form-control input-sm';
        sel.id = 'id_years';
        sel.style.display = 'none';
        for(const yr of keys.sort((a, b) => { return b - a; })) {
            const el = document.createElement('option');
            el.textContent = yr;
            el.value = yr;
            sel.appendChild(el);
        }
        document.getElementById('id_date').parentElement.appendChild(sel);
    };

    const initProfileFilter = (controller, conf) => {
        const onFilterChange = () => {
            const bits = HashBits.fromFilters();
            console.log(bits);
            bits.update();
            controller.filterLogs(bits);
        };
        const onHashChange = () => {
            const bits = HashBits.fromHash();
            setFilterFields(bits);
            controller.filterLogs(bits);
        };
        const dateEl = document.getElementById('id_date');
        //new Pikaday({
        //    field: dateEl,
        //    format: DATE_FORMAT,
        //    minDate: new Date(1920,1,1),
        //    yearRange: [1920, (new Date()).getFullYear()],
        //    onSelect: dt => { console.log(dt, this); }
        //});

        window.addEventListener('hashchange', onHashChange, false);
        document.getElementById('id_timeframe').addEventListener('change', () => {
            if(this.value === '=') {
                document.getElementById('id_years').style.display = 'inline-block';
                dateEl.style.display = 'none';
            }
            else {
                dateEl.style.display = 'inline-block';
                document.getElementById('id_years').style.display = 'none';
            }
        }, false);

        dateEl.addEventListener('input', onFilterChange, false);
        dateEl.addEventListener('propertychange', onFilterChange, false);
        for(const e of document.querySelectorAll('.filter_ctrl')) {
            e.addEventListener('change', onFilterChange, false);
        }

        onHashChange();
    };

    const controller = {
        initialize(entities, logs, conf) {
            const countries = {};
            const yearSet = {};
            const summary = new Summary();
            const entityDict = {};
            this.logEntries = [];
            for(const entity of entities) {
                const e = new LogEntry(entity);
                this.logEntries.push(e);
                if(e.country_code) {
                    countries[e.country_code] = e.country_name;
                }
                entityDict[e.id] = e;
            }
            for(const log of logs) {
                log.entity = entityDict[log.entity];
                if(!log.entity) { console.log(log); }

                log.entity.logs.push(log);
                log.arrival = moment(log.arrival);
                log.isActive = true;
                yearSet[log.arrival.year()] = true;
                summary.add(log.entity);
            }

            this.logs = new TravelLogs(logs, summary);
            console.log(summary);
            createCountryOptions(countries);
            initOrderingByColumns(this);
            createYearsOption(Object.keys(yearSet));
            initProfileFilter(this, conf);
        },
        filterLogs(bits) {
            this.logs.filter(bits);
            showLogs(this.logs);
        },
        sortLogs(column, order) {
            this.logs.sortLogs(column, order);
            showLogs(this.logs);
        }
    };

    class HashBits {
        static fromHash(hash) {
            const bits = new HashBits();
            hash = hash || window.location.hash;
            if(hash && hash[0] == '#') {
                hash = hash.substr(1);
            }

            if(hash) {
                for(const bit of hash.split('/')) {
                    const kvp = bit.split(':');
                    bits[kvp[0]] = (kvp.length === 2) ? kvp[1] : true;
                }

                if(bits.date) {
                    bits.timeframe = bits.date[0];
                    bits.date = (bits.timeframe === '=')
                              ? parseInt(bits.date.substr(1))
                              : moment(bits.date.substr(1));
                }
            }
            return bits;
        }
        static fromFilters() {
            const bits = new HashBits();
            const dt = document.getElementById('id_date').value;
            const el = document.querySelector('#history thead .current');
            bits.type = document.getElementById('id_filter').value;
            bits.co   = document.getElementById('id_co').value;
            bits.timeframe = document.getElementById('id_timeframe').value;
            bits.limit = document.getElementById('id_limit').value;

            if(bits.timeframe === '=') {
                bits.date = parseInt(document.getElementById('id_years').value);
            }
            else if(bits.timeframe) {
                bits.date = dt ? moment(dt) : null;
            }
            if(el && el.dataset.order == 'asc') {
                bits.asc = el.dataset.column;
            }
            return bits;
        }
        toString() {
            let a = [];
            for(const bit of ['type', 'co', 'asc', 'limit']) {
                if(this[bit]) {
                    a.push(bit + ':' + this[bit]);
                }
            }
            if(this.timeframe === '-' || this.timeframe === '+') {
                if(this.date) {
                    a.push('date:' + this.timeframe + this.date.format(DATE_FORMAT));
                }
            }
            else if(this.timeframe === '=') {
                if(this.date) {
                    a.push('date:' + this.timeframe + this.date);
                }
            }
            return a.length ? '#' + a.join('/') : './';
        }
        update() {
            window.history.pushState({}, '', this.toString());
        }
    }

    const setFilterFields = bits => {
        const yearsEl = document.getElementById('id_years');
        const dateEl = document.getElementById('id_date');
        document.getElementById('id_filter').value = bits.type || '';
        document.getElementById('id_timeframe').value = bits.timeframe || '';
        document.getElementById('id_co').value = bits.co || '';
        document.getElementById('id_limit').value = bits.limit || '';

        yearsEl.style.display = 'none';
        dateEl.style.display = 'none';
        if((bits.timeframe === '=') && bits.date) {
            yearsEl.value = bits.date;
            yearsEl.style.display = 'inline-block';
        }
        else {
            if(bits.timeframe && bits.date) {
                dateEl.value = bits.date.format(DATE_FORMAT);
                dateEl.style.display = 'inline-block';
            }
        }
    };

    const loadLogs = () => {
        const path = window.location.pathname;
        const m = path.match(/\/([^\/]+)\/?$/);
        if(m) {
            fetch(`/api/v1/logs/${m[1]}/`)
                .then(response => response.json())
                .then(data => controller.initialize(data.entities, data.logs, {'mediaPrefix': ''}));
        }
    };

    return {
        loadLogs: loadLogs,
        parseHash: hash => HashBits.fromHash(hash),
        controller: controller,
    };
}(window));
