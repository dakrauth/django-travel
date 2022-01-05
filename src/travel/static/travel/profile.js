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
const MISSING_FLAG = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-geo-alt-fill" viewBox="0 0 16 16"><path d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10zm0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"/></svg>'
const DATE_FORMAT  = 'YYYY-MM-DD';
const TYPE_MAPPING = {
    'cn': 'Continents', 'co': 'Countries', 'wh': 'World Heritage',
    'st': 'States',     'ap': 'Airports',  'np': 'National Parks',
    'lm': 'Landmarks',  'ct': 'Cities'
};

const renderTemplate = function(templateId, data) {
    const template = document.getElementById(templateId);
    const node = template.content.cloneNode(true);
    data = data || {};
    for(const [key, value] of Object.entries(data)) {
        const el = node.querySelector(`.${key}`)
        if(el) {
            if(value === undefined || value === null) {
                el.remove();
            }
            else {
                el.textContent = value.toString();
            }
        }
    }
    return node;
};

class Summary {
    constructor(grandTotal) {
        this.types = {}
        this.grandTotal = grandTotal;
        for(const key of Object.keys(TYPE_MAPPING)) {
            this.types[key] = {};
        }
    }
    add(e) {
        const kind = this.types[e.type_abbr];
        kind[e.id] = 1 + (kind[e.id] || 0);
    }
}

class HashBits {
    static fromHash(hash) {
        const bits = new HashBits();
        hash = hash || window.location.hash;
        if(hash && hash[0] == '#') {
            hash = hash.substr(1);
        }

        if(hash) {
            for(const bit of hash.split('/')) {
                const [k, v] = bit.split(':');
                bits[k] = v;
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
        const el = document.querySelector('#history thead .current');
        document.querySelectorAll('.profile-filter [data-filter]').forEach(
            el => bits[el.dataset.filter] = el.value
        );

        if(bits.timeframe === '=') {
            bits.date = parseInt(bits.year);
        }
        else if(bits.timeframe) {
            bits.date = bits.date ? moment(bits.date) : null;
        }
        if(el && el.dataset.order) {
            bits[el.dataset.order] = el.dataset.column;
        }
        return bits;
    }
    toString() {
        let a = [];
        for(const bit of ['type', 'co', 'asc', 'desc', 'limit']) {
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

const parseHash = hash => HashBits.fromHash(hash);

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
        this.sorters = {
            type: (a, b) => (b.entity.type_abbr > a.entity.type_abbr) ? 1: -1,
            name: (a, b) => (b.entity.name > a.name) ? 1 : -1,
            recent_visit: (a, b) => b.arrival.valueOf() - a.arrival.valueOf(),
            first_visit: (a, b) => {
                const aLogs = a.entity.logs;
                const bLogs = b.entity.logs;
                return (
                    bLogs[bLogs.length - 1].arrival.valueOf() -
                    aLogs[aLogs.length - 1].arrival.valueOf()
                );
            },
            num_visits: (a, b) => b.entity.logs.length - a.entity.logs.length,
            rating: (a, b) => a.rating - b.rating
        };

    }
    sortLogs(column, order) {
        console.log('ordering', column, order);
        this.logs.sort(this.sorters[column]);
        if(order === 'desc') {
            this.logs.reverse()
        }
    }
    filter(bits) {
        console.log('filter bits', bits);
        this.summary = new Summary(this.logs.length);
        for(const log of this.logs) {
            ++this.summary.total;
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

class View {
    constructor() {
        this.dateEl = document.getElementById('id_date');
        this.yearEl = document.getElementById('id_year')
    }
    getOrdering(el) {
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
    }
    initOrderingByColumns(handler) {
        for(const e of document.querySelectorAll('#history thead th[data-column]')) {
            e.addEventListener('click', handler, false)
        };
    }
    createCountryOptions(countries) {
        const cos = document.getElementById('id_co');
        for(const key of Object.keys(countries).sort()) {
            const el = document.createElement('option');
            el.textContent = countries[key];
            el.value = key;
            cos.appendChild(el);
        }
    }
    createYearsOption(keys) {
        for(const yr of keys.sort((a, b) => { return b - a; })) {
            const el = document.createElement('option');
            el.textContent = yr;
            el.value = yr;
            this.yearEl.appendChild(el);
        }
    }
    initProfileFilter(filterHandler) {
        document.getElementById('id_timeframe').addEventListener('change', (evt) => {
            const value = evt.target.value;
            if(value === '=') {
                this.dateEl.style.display = 'none';
                this.yearEl.style.display = 'inline-block';
            }
            else if (value === '') {
                this.dateEl.style.display = 'none';
                this.yearEl.style.display = 'none';
            }
            else {
                this.yearEl.style.display = 'none';
                this.dateEl.style.display = 'inline-block';
            }
        }, false);

        this.dateEl.addEventListener('input', filterHandler, false);
        this.dateEl.addEventListener('propertychange', filterHandler, false);
        for(const e of document.querySelectorAll('.filter-ctrl')) {
            e.addEventListener('change', filterHandler, false);
        }
    }
    setFilterFields(bits) {
        document.getElementById('id_filter').value = bits.type || '';
        document.getElementById('id_timeframe').value = bits.timeframe || '';
        document.getElementById('id_co').value = bits.co || '';
        document.getElementById('id_limit').value = bits.limit || '';

        this.yearEl.style.display = 'none';
        this.dateEl.style.display = 'none';
        if((bits.timeframe === '=') && bits.date) {
            this.yearEl.value = bits.date;
            this.yearEl.style.display = 'inline-block';
        }
        else {
            if(bits.timeframe && bits.date) {
                this.dateEl.value = bits.date.format(DATE_FORMAT);
                this.dateEl.style.display = 'inline-block';
            }
        }
    }
    createLogRow(log) {
        let extras = [];
        const e = log.entity;
        const firstArrival = e.logs[e.logs.length-1].arrival;
        const dateFormat  = 'MMM Do YYYY ddd h:ssa';
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
    }
    showLogs(travelLogs) {
        console.time('showLogs');
        const count = travelLogs.logs.length;
        let parent = document.getElementById('history');
        let el = parent.querySelector('tbody');

        el.parentNode.removeChild(el);
        el = document.createElement('tbody');

        console.time('createLogRows');
        let total = 0
        for(const log of travelLogs.logs) {
            if(log.isActive) {
                ++total;
                el.appendChild(this.createLogRow(log));
            }
        }
        console.timeEnd('createLogRows');

        parent.appendChild(el);
        this.renderSummary(travelLogs.summary, total);
        console.timeEnd('showLogs');
    }
    renderSummary(summary, total) {
        const countEl = document.getElementById('id_count')
        let label = 'entr' + (summary.grandTotal > 1 ? 'ies' : 'y');
        if(summary.grandTotal === total) {
            countEl.textContent = `${total} ${label}`;
        }
        else {
            countEl.textContent = `${total} of ${summary.grandTotal} ${label}`;
        }

        const el = document.getElementById('summary');
        while(el.lastChild) {
          el.removeChild(el.lastChild);
        }

        for(const key of Object.keys(summary.types)) {
            const items = Object.keys(summary.types[key]).length;
            if(items) {
                const span = document.createElement('span');
                span.className = 'badge bg-light me-1 mb-1 border';
                span.innerHTML = TYPE_MAPPING[key];

                const counter = document.createElement('span');
                counter.className = 'badge rounded-pill bg-danger ms-1';
                counter.textContent = items;
                span.appendChild(counter);
                el.appendChild(span);
            }
        }
    }
}

const loadData = async (url) => {
    const response = await fetch(url);
    const data = await response.json();
    return data;
};


class LogModels {
    constructor(data) {
        this.countries = {};
        this.yearSet = {};
        this.logs = data.logs;
        this.summary = new Summary(this.logs.length);
        this.logEntries = [];

        const entityDict = {};
        for(const entity of data.entities) {
            const e = new LogEntry(entity);
            this.logEntries.push(e);
            if(e.country_code) {
                this.countries[e.country_code] = e.country_name;
            }
            entityDict[e.id] = e;
        }
        for(const log of data.logs) {
            log.entity = entityDict[log.entity];
            if(!log.entity) { console.warn('Unknown log entity', log); }

            log.entity.logs.push(log);
            log.arrival = moment(log.arrival);
            log.isActive = true;
            this.yearSet[log.arrival.year()] = true;
            this.summary.add(log.entity);
        }

        this.logs = new TravelLogs(data.logs, this.summary);
        console.log(this.summary);
    }
}

class Controller  {
    constructor(models, view) {
        this.models = models;
        this.view = view;
        this.view.createCountryOptions(this.models.countries);
        this.view.createYearsOption(Object.keys(this.models.yearSet));

        this.view.initOrderingByColumns((evt) => {
            const ordering = this.view.getOrdering(evt.target);
            if(ordering.order === 'asc') {
                HashBits.fromFilters().update();
            }
            this.sortLogs(ordering.column, ordering.order);
        });

        this.view.initProfileFilter(() => {
            const bits = HashBits.fromFilters();
            console.log(bits);
            bits.update();
            this.filterLogs(bits);
        });

        window.addEventListener('hashchange', (evt) => {
            const bits = HashBits.fromHash();
            this.view.setFilterFields(bits);
            this.filterLogs(bits);
        }, false);
        window.dispatchEvent(new Event('hashchange'));

    }
    filterLogs(bits) {
        this.models.logs.filter(bits);
        this.view.showLogs(this.models.logs);
    }
    sortLogs(column, order) {
        this.models.logs.sortLogs(column, order);
        this.view.showLogs(this.models.logs);
    }
};

const loadLogs = async (url) => {
    const data = await loadData(url);
    const controller = new Controller(
        new LogModels(data),
        new View()
    );
    return controller;
};

export {loadLogs, parseHash};
