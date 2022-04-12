ip = window.location.hostname
let socket = new WebSocket("ws://" + ip);
let update_timer

function start_update(socket) {
    update_timer = setInterval(function () { socket.send('update_data'); }, 1000);
};

socket.onopen = function (event) {
    start_update(socket)
};

socket.onmessage = function (event) {
    document.getElementById("secs").innerText = event.data
};

socket.onclose = function (event) {
    clearInterval(update_timer)
};