const travelTzDelta = function(loc, there) {
    let delta = there.utcOffset() - loc.utcOffset();
    let delta_str = '';
    const neg = delta < 0;
    delta = Math.abs(delta);
    if(delta) {
        let minutes = delta % 60;
        if(delta >= 60) {
            delta_str = Math.floor(delta / 60) + ' hours';
        }
        if(minutes) {
            delta_str += (delta_str.length ? ' ' : '') + minutes + ' minutes';
        }
        delta_str = ' (' + (neg ? '-' : '+') + delta_str + '/local)';
    }
    return delta_str;
};

export const updateTravelTimestamps = function() {
    document.querySelectorAll('.tz-clock').forEach(function(el) {
        const tz = el.getAttribute('data-timezone');
        const loc = moment();
        const there = loc.clone().tz(tz);
        el.textContent = there.format('MMMM Do YYYY, h:mm:ss a') + travelTzDelta(loc, there);
    });
    setTimeout(updateTravelTimestamps, 1000)
};
