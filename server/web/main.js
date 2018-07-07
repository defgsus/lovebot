
var ws = new WebSocket("ws://127.0.0.1:8001/ws");

ws.onopen = function() {
    console.log("opened", ws);
    ws.send("from webpage");
};

ws.onmessage = function (evt) {
    console.log(evt.data);
};