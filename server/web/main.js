
var websocket = null;

function connect_to_websocket() {

    websocket = new WebSocket("ws://127.0.0.1:8001/ws");

    websocket.onopen = function() {
        send_command("get_world");
        send_command("create_bot");
        send_command("get_bots");
    };

    websocket.onmessage = function (evt) {
        var data = JSON.parse(evt.data);
        if (data.event)
            log_event(data.event);
        log(data, "from-server");
    };
}

function send_command(cmd) {
    var msg = JSON.stringify({cmd: cmd});
    log(msg, "to-server");
    websocket.send(msg);
}

function log(msg, klass) {
    var ts = "";
    if (typeof msg === "object") {
        if (msg.ts !== undefined)
            ts = msg.ts;
        msg = JSON.stringify(msg);
    }
    var html = "<div";
    if (klass)
        html += ' class="'+klass+'"';
    html += ">"+ts+": "+msg+"</div>";
    $(".log-window").prepend($(html));
}

function log_event(event) {
    var msg = JSON.stringify(event.data);
    var html = "<div>"+event.ts+": "+event.name+": "+msg+"</div>";
    $(".event-log-window").prepend(html);
}

$(function() {

    connect_to_websocket();

});
