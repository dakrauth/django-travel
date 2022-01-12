const travelTzDelta = function(delta) {
    let delta_str = '';
    const neg = delta < 0 ? '-' : '+';
    delta = Math.abs(delta);
    if(delta) {
        let minutes = delta % 60;
        if(delta >= 60) {
            delta_str = Math.floor(delta / 60) + ' hours';
        }
        if(minutes) {
            delta_str += (delta_str.length ? ' ' : '') + minutes + ' minutes';
        }
        delta_str = ` (${neg}${delta_str})`;
    }
    return delta_str;
};

export const updateTravelTimestamps = function() {
    document.querySelectorAll('.tz-clock').forEach(function(el) {
        const tz = el.getAttribute('data-timezone');
        const here = luxon.DateTime.now();
        const away = here.setZone(tz);
        
        const value = away.toFormat('DDDD, TTT') + travelTzDelta(away.offset - here.offset);
        el.textContent = value;
    });
    setTimeout(updateTravelTimestamps, 1000)
};
