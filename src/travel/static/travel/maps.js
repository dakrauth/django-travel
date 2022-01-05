const bisectArray = function(array, val) {
    var idx = 0;
    if (array.length === 0) {
        return 0;
    }
    for (; idx < array.length; idx++) {
        if(val > array[idx]) {
            return idx;
        }
    }
    return idx;
};

const ZOOM_AREA_ARRAY = [9765625, 1953125, 390625, 78125, 15625, 3125, 625, 125, 25, 5];
const DEFAULT_ZOOM_LEVELS = {
    st: 8,
    cn: 4,
    wh: 13,
    lm: 9,
    np: 13,
    ap: 11,
    co: 10,
    ct: 13
};

const getZoomValue = function(type, area) {
    area = parseInt(area);
    if(!area) {
        return DEFAULT_ZOOM_LEVELS[type];
    }

    return 4 + bisectArray(ZOOM_AREA_ARRAY, area);
};

const googleMapUrl = function(attrs) {
    const zoom = getZoomValue(attrs.type, attrs.area);
    return attrs.coords ? `https://www.google.com/maps/@${attrs.coords},${zoom}z` : null;
};


export const makeEntityMap = function(src) {
    document.querySelectorAll(src).forEach(el => {
        const href = googleMapUrl({...el.dataset})
        if(href) {
            el.href = href;
        }
    });
};
