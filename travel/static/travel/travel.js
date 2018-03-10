//------------------------------------------------------------------------------
// Sample entity object
//------------------------------------------------------------------------------
// entity = {
//     "flag__svg": "img/wh-32.png",
//     "code": "3",
//     "name": "Aachen Cathedral",
//     "locality": "State of North Rhine-Westphalia (Nordrhein-Westfalen)",
//     "country__flag__svg": "img/flags/co/de/de-32.png",
//     "country__code": "DE",
//     "country__name": "Germany",
//     "type__abbr": "wh",
//     "id": 11942
// }
//}
//------------------------------------------------------------------------------

;var Travelogue = (function(root) {
    var TYPE_MAPPING = {
        'cn': 'Continents', 'co': 'Countries', 'wh': 'World Heritage sites',
        'st': 'States',     'ap': 'Airports',  'np': 'National Parks',
        'lm': 'Landmarks',  'ct': 'Cities'
    };
    
    var sorters = {
        'type': function(a, b) {
            return (b.entity.type__abbr > a.entity.type__abbr) ? 1: -1;
        },
        'name': function(a, b) {
            return (b.entity.name > a.name) ? 1 : -1;
        },
        'recent_visit': function(a, b) {
            return b.arrival.valueOf() - a.arrival.valueOf();
        },
        'first_visit':  function(a, b) {
            a = a.entity.logs;
            b = b.entity.logs;
            return b[b.length - 1].arrival.valueOf() - a[a.length - 1].arrival.valueOf();
        },
        'num_visits':   function(a, b) {
            return b.entity.logs.length - a.entity.logs.length;
        },
        'rating': function(a, b) {
            return a.rating - b.rating;
        }
    };
    
    var DATE_STRING  = 'MMM Do YYYY';
    var TIME_STRING  = 'ddd h:ssa';
    var MEDIA_PREFIX = '/media/';
    var DATE_FORMAT  = 'YYYY-MM-DD';
    var STARS        = '★★★★★';

    var stars = function(rating) { return STARS.substr(rating - 1); };
    
    var DOM = {
        get: function(q, ctx) { return document.querySelector(q, ctx); },
        create: function(tag) {
            var j, key, arg;
            var el = document.createElement(tag);
            for(var i = 1; i < arguments.length; i++) {
                arg = arguments[i];
                if(Array.isArray(arg)) {
                    Array.from(arg).forEach(function(child) {
                        el.appendChild(child);
                    });
                }
                else if(typeof arg === 'string') {
                    el.textContent = arg;
                }
                else {
                    Object.keys(arg).forEach(function(key) {
                        el.setAttribute(key, arg[key]);
                    });
                }
            }
            return el;
        }
    };
    
    var dateTags = function(dtw) {
        return [
            DOM.create('div', dtw.format(DATE_STRING)),
            DOM.create('div', dtw.format(TIME_STRING))
        ];
    };
    
    var createLogRow = function(log) {
        var e = log.entity;
        var nameTd = DOM.create('td');
        var flagTd = DOM.create('td');
        var extras = [];
        var firstArrival = e.logs[e.logs.length-1].arrival;
        var attrs = {
            'data-id': e.id,
            'data-name': e.name,
            'data-arrival': log.arrival.valueOf(),
            'data-first': firstArrival.valueOf(),
            'data-count': e.logs.length,
            'data-rating': log.rating,
            'class': e.type__abbr + ' co-' + (
                e.country__code ?
                e.country__code :
                (e.type__abbr == 'co' ? e.code : '')
            )
        };

        nameTd.appendChild(DOM.create('a', e.name, {'href': e.url()}));
        if(e.flag__svg) {
            flagTd.appendChild(DOM.create('img', {'src': e.flag__svg, 'class': 'flag flag-sm'}));
        }
        
        e.locality && extras.push(e.locality);
        e.country__name && extras.push(e.country__name);
        if(extras.length) {
            nameTd.appendChild(DOM.create('span', extras.join(', ')));
        }
        
        if(e.country__flag__emoji) {
            nameTd.appendChild(DOM.create('span', e.country__flag__emoji));    
        }
        else if(e.country__flag__svg) {
            nameTd.appendChild(DOM.create('img', {
                'src': e.country__flag__svg,
                'class': 'flag flag-xs'
            }));
        }

        return DOM.create('tr', attrs, [
            flagTd,
            DOM.create('td', TYPE_MAPPING[e.type__abbr]),
            nameTd,
            DOM.create('td', {'class': 'when'}, dateTags(log.arrival)),
            DOM.create('td', {'class': 'when'}, dateTags(firstArrival)),
            DOM.create('td', e.logs.length.toString()),
            DOM.create('td', stars(log.rating))
        ]);
    };
    
    var getOrdering = function(el) {
        var ordering = {'column': el.dataset.column, 'order': el.dataset.order};
        var current = el.parentElement.querySelector('.current');
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
    
    var showSummary = function(summary) {
        var el = DOM.get('#summary');
        while(el.lastChild) {
          el.removeChild(el.lastChild);
        }

        el.appendChild(DOM.create('strong', 'Summary: '));
        Object.keys(summary).forEach(function(key) {
            var items = Object.keys(summary[key]).length;
            if(items) {
                el.appendChild(DOM.create(
                    'span',
                    {'class': 'label label-info'},
                    TYPE_MAPPING[key] + ': ' + items
                ));
            }
        });
    };
    
    var Summary = Object.create({
        init: function() {
            Object.keys(TYPE_MAPPING).forEach(function(key) {
                this[key] = {};
            }, this);
            return this;
        },
        add: function(e) {
            var kind = this[e.type__abbr];
            kind[e.id] = 1 + (kind[e.id] || 0);
        }
    });

    var LogEntry = Object.create({
        init: function(e, mediaPrefix) {
            Object.assign(this, e);
            this.logs = [];
            if(this.flag__svg) {
                this.flag__svg = mediaPrefix + this.flag__svg;    
            }
            
            if(this.country__flag__svg) {
                this.country__flag__svg = mediaPrefix + this.country__flag__svg;
            }
            return this;
        },
        url: function() {
            var bit = this.code;
            if(this.type__abbr == 'wh' || this.type__abbr == 'st') {
                bit = this.country__code + '-' + bit;
            } 
            return '/i/' + this.type__abbr + '/' + bit + '/';
        }
    });
    
    var TravelLogs = Object.create({
        init: function(logs, summary) {
            this.logs = logs;
            this.summary = summary;
            return this;
        },
        sortLogs: function(column, order) {
            console.log('ordering', column, order);
            this.logs.sort(sorters[column]);
            if(order === 'desc') {
                this.logs.reverse()
            }
        },
        filter: function(bits) {
            var summary = this.summary;
            console.log('filter bits', bits);
            if(bits.type || bits.co || bits.timeframe || bits.limit) {
                summary = Object.create(Summary).init();
                this.logs.forEach(function(log) {
                    var e = log.entity;
                    var good = true;
                    if(bits.type) {
                        good = (e.type__abbr === bits.type);
                    }

                    if(good && bits.co) {
                        good = (
                            e.country__code === bits.co ||
                            (e.type__abbr === 'co' && e.code === bits.co)
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
                        summary.add(e);
                    }
                    
                    log.isActive = good;
                });
            }
            return this;
        }
    });
    var showLogs = function(travelLogs) {
        var count = travelLogs.logs.length;
        var parent = DOM.get('#history');
        var el = parent.querySelector('tbody');
        var start = new Date();
        
        DOM.get('#id_count').textContent = (count + ' entr' + (count > 1 ? 'ies' : 'y'));
        el.parentNode.removeChild(el);
        el = DOM.create('tbody');
        travelLogs.logs.forEach(function(log) {
            if(log.isActive) {
                el.appendChild(createLogRow(log));    
            }
            
        });
        parent.appendChild(el);
        showSummary(travelLogs.summary);
        console.log('delta', new Date() - start);
    };
    
    var initOrderingByColumns = function(history) {
        var columns = '#history thead th[data-column]';
        Array.from(document.querySelectorAll(columns)).forEach(function(e) {
            e.addEventListener('click', function(evt) {
                var ordering = getOrdering(this);
                if(ordering.order === 'asc') {
                    HashBits.fromFilters().update();
                }
                history.sortCurrent(ordering.column, ordering.order);
            }, false);
        });
    };

    var createCountryOptions = function(countries) {
        var cos = DOM.get('#id_co');
        Object.keys(countries).sort().forEach(function(key) {
            cos.appendChild(DOM.create('option', countries[key], {'value': key}));
        });
    };
    
    var createYearsOption = function(keys) {
        var sel = DOM.create('select', {
            'class': 'filter_ctrl form-control input-sm',
            'id': 'id_years'
        });

        sel.style.display = 'none';
        keys.sort(function(a, b) { return b - a; }).forEach(function(yr) {
            sel.appendChild(DOM.create('option', yr, {'value': yr}));
        });
        DOM.get('#id_date').parentElement.appendChild(sel);
    };

    var initProfileFilter = function(conf) {
        var dateEl = DOM.get('#id_date');
        var picker = new Pikaday({
            field: dateEl,
            format: DATE_FORMAT,
            minDate: new Date(1920,1,1),
            yearRange: [1920, (new Date()).getFullYear()],
            onSelect: function(dt) { console.log(dt, this); }
        });

        window.addEventListener('hashchange', onHashChange, false);
        DOM.get('#id_timeframe').addEventListener('change', function() {
            if(this.value === '=') {
                DOM.get('#id_years').style.display = 'inline-block';
                dateEl.style.display = 'none';
            }
            else {
                dateEl.style.display = 'inline-block';
                DOM.get('#id_years').style.display = 'none';
            }
        }, false);

        dateEl.addEventListener('input', onFilterChange, false);
        dateEl.addEventListener('propertychange', onFilterChange, false);
        Array.from(document.querySelectorAll('.filter_ctrl')).forEach(function(e) {
            e.addEventListener('change', onFilterChange, false);
        });

        onHashChange();
    };
    
    var controller = {
        initialize: function(entities, logs, conf) {
            var mediaPrefix = conf.mediaPrefix || MEDIA_PREFIX;
            var countries = {};
            var yearSet = {};
            var summary = Object.create(Summary).init();
            var entityDict = {};
            this.logEntries = [];
            entities.forEach(function(e) {
                var e = Object.create(LogEntry).init(e, mediaPrefix);
                this.logEntries.push(e);
                if(e.country__code) {
                    countries[e.country__code] = e.country__name;
                }
                entityDict[e.id] = e;
            }, this);
            
            logs = logs.map(function(log) {
                log.entity = entityDict[log.entity__id];
                if(!log.entity) { console.log(log); }
                log.entity.logs.push(log);
                log.arrival = moment(log.arrival.value);
                log.isActive = true;
                yearSet[log.arrival.year()] = true;
                summary.add(log.entity);
                return log;
            }, this);
            
            this.logs = Object.create(TravelLogs).init(logs, summary);
            console.log(summary);
            createCountryOptions(countries);
            initOrderingByColumns(this);
            createYearsOption(Object.keys(yearSet));
            initProfileFilter(conf);
        },
    
        filterLogs: function(bits) {
            this.logs.filter(bits);
            showLogs(this.logs);
        },
    
        sortLogs: function(column, order) {
            this.logs.sortLogs(column, order);
            showLogs(this.logs);
        }
    };
        
    var onFilterChange = function() {
        var bits = Object.create(HashBits).fromFilters();
        console.log(bits);
        bits.update();
        controller.filterLogs(bits);
    };

    var onHashChange = function() {
        var bits = HashBits.fromHash();
        setFilterFields(bits);
        controller.filterLogs(bits);
    };
        
    var HashBits = Object.create({
        fromHash: function(hash) {
            hash = hash || window.location.hash;
            if(hash && hash[0] == '#') {
                hash = hash.substr(1);
            }
            
            if(hash) {
                hash.split('/').forEach(function(bit) {
                    var kvp = bit.split(':');
                    this[kvp[0]] = (kvp.length === 2) ? kvp[1] : true;
                }, this);

                if(this.date) {
                    this.timeframe = this.date[0];
                    this.date = (this.timeframe === '=') ? 
                        parseInt(this.date.substr(1))    :
                        moment(this.date.substr(1));
                }
            }
            return this;
        },
        fromFilters: function() {
            var dt    = DOM.get('#id_date').value;
            var el    = document.querySelector('#history thead .current');
            this.type = DOM.get('#id_filter').value;
            this.co   = DOM.get('#id_co').value;
            this.timeframe = DOM.get('#id_timeframe').value;
            this.limit = DOM.get('#id_limit').value;

            if(this.timeframe === '=') {
                this.date = parseInt(DOM.get('#id_years').value);
            }
            else if(this.timeframe) {
                this.date = dt ? moment(dt) : null;
            }
            if(el && el.dataset.order == 'asc') {
                this.asc = el.dataset.column;
            }
            return this;
        },
        toString: function() {
            var a = [];
            ['type', 'co', 'asc', 'limit'].forEach(function(bit) {
                if(this[bit]) {
                    a.push(bit + ':' + this[bit]);
                }
            }, this);

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
        },
        update: function() {
            window.history.pushState({}, '', this.toString());
        }
    });
    
    var setFilterFields = function(bits) {
        var yearsEl = DOM.get('#id_years');
        var dateEl = DOM.get('#id_date');
        DOM.get('#id_filter').value = bits.type || '';
        DOM.get('#id_timeframe').value = bits.timeframe || '';
        DOM.get('#id_co').value = bits.co || '';
        DOM.get('#id_limit').value = bits.limit || '';

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
    
    return {
        parseHash: function(hash) {
            return Object.create(HashBits).fromHash(hash);
        },
        timeit: function(fn) {
            var args = Array.from(arguments);
            var start, end, result;
            args.shift();
            start = new Date();
            result = fn.call(undefined, args);
            end = new Date();
            console.log(start + ' | ' + end + ' = ' + (end - start));
            return result;
        },
        DOM: DOM,
        controller: controller,
        profileHistory: function(entities, logs, conf) {
            controller.initialize(entities, logs, conf);
        }
    };
}(window));
