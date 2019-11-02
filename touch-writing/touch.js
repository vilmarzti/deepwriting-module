let canvas;
let ctx;
let offset_x;
let offset_y;
let ismousedown = false
let touchstart_pos;
let touchmove_pos;

let touchhistory = [];

window.onload = () => {
    canvas = document.getElementsByTagName('canvas')[0];
    ctx = canvas.getContext('2d');
    offset_x = canvas.offsetLeft;
    offset_y = canvas.offsetTop;
    canvas.addEventListener('touchstart', touchstart);
    canvas.addEventListener('touchmove', touchmove);
    canvas.addEventListener('touchend', touchend);
    canvas.addEventListener('mousedown', mousedown);
    canvas.addEventListener('mousemove', mousemove);
    canvas.addEventListener('mouseup', mouseup)
}


function mousedown(event) {
    ismousedown = true;
    let new_event = mouseToTouch(event);
    touchstart(new_event)
}

function mousemove(event) {
    if (ismousedown) {
        let new_event = mouseToTouch(event);
        touchmove(new_event)
    }
}

function mouseup(event) {
    let new_event = mouseToTouch(event);
    ismousedown = false;
    touchend(new_event);
}

function touchstart(event) {
    touchstart_pos = getRelativePosition(getTouches(event));
    touchhistory.push(
        touch_event('start', touchstart_pos[0], touchstart_pos[1], 0)
    )
}

function touchmove(event) {
    touchmove_pos = getRelativePosition(getTouches(event));
    ctx.beginPath();
    ctx.moveTo(touchstart_pos[0], touchstart_pos[1]);
    ctx.lineTo(touchmove_pos[0], touchmove_pos[1]);
    ctx.stroke();
    ctx.strokeStyle = "black";
    touchhistory.push(
        touch_event('move', touchmove_pos[0], touchmove_pos[1], 0)
    );
    touchstart_pos = touchmove_pos;
}

function touchend(event) {
    let touchend_pos = getRelativePosition(getTouches(event));
    ctx.beginPath();
    ctx.moveTo(touchstart_pos[0], touchstart_pos[1]);
    ctx.lineTo(touchmove_pos[0], touchmove_pos[1]);
    ctx.stroke();
    ctx.strokeStyle = "black";
    touchhistory.push(
        touch_event('end', touchend_pos[0], touchend_pos[1], 1)
    );
}

function touch_event(type, x, y, pen) {
    return {
        'type': type,
        'x': x,
        'y': y,
        'ev': pen,
        'ts': (new Date()).getTime()
    }
}

function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    touchhistory = []
}

function download() {
    let object = {};
    object['test2'] = {};
    object['test2']['wholeword_segments'] = "";
    object['test2']['word_ascii'] = "";
    object['test2']['word_stroke'] = touchhistory;

    // save
    data = "text/json;charset=utf-8, " + encodeURIComponent(JSON.stringify(object));
    let a = document.createElement('a');
    a.href = 'data:' + data;
    a.download = 'hello_world.json'
    a.innerHTML = 'Download'
    a.click()
}

function getRelativePosition([x, y]) {
    return [x - offset_x, y - offset_y];
}

function mouseToTouch(event) {
    event.touches = []
    event.touches.push({
        "clientX": event.clientX,
        "clientY": event.clientY
    }
    )
    return event
}

function getTouches(event) {
    return [event.touches[0].clientX, event.touches[0].clientY];
}