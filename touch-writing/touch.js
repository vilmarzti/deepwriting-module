let canvas;
let ctx;
let offset_x;
let offset_y;
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
}



function touchstart(event){
    touchstart_pos = getRelativePosition(getTouches(event));
    touchhistory.push({'type': 'touchstart', 'x': touchmove_pos[0], 'y': touchmove_pos[1]})
}

function touchmove(event){
    touchmove_pos = getRelativePosition(getTouches(event));
    ctx.beginPath();
    ctx.moveTo(touchstart_pos[0], touchstart_pos[1]);
    ctx.lineTo(touchmove_pos[0], touchmove_pos[1]);
    ctx.stroke();
    ctx.strokeStyle = "black";
    touchhistory.push({'type': 'touchmove', 'x': touchmove_pos[0], 'y': touchmove_pos[1]})
    touchstart_pos = touchmove_pos;
}

function touchend(event){
    touchend_pos = getRelativePosition(getTouches(event));
    ctx.beginPath();
    ctx.moveTo(touchstart_pos[0], touchstart_pos[1]);
    ctx.lineTo(touchmove_pos[0], touchmove_pos[1]);
    ctx.stroke();
    ctx.strokeStyle = "black";
    touchhistory.push({'type': 'end', 'x': touchmove_pos[0], 'y': touchmove_pos[1]})
}

function clearCanvas(){
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    touchhistory = []
}

function getRelativePosition([x, y]){
    return [x-offset_x, y-offset_y];
}

function getTouches(event){
    return [event.touches[0].clientX, event.touches[0].clientY];
}