
var websocket = null;

var API = {
    get_world: function () {
        send_command("get_world");
    },
    get_bots: function () {
        send_command("get_bots");
    },
    get_connections: function () {
        send_command("get_connections");
    },
    create_bot: function (name) {
        send_command("create_bot", {name: name});
    },
    set_wheel_speed: function(bot_id, left, right) {
        send_command("set_wheel_speed", {id: bot_id, speed: [left, right]})
    }
};


function connect_to_websocket() {

    websocket = new WebSocket("ws://127.0.0.1:8001/ws");

    websocket.onopen = function() {
        /*API.get_connections();
        API.get_world();
        API.create_bot("Viktor");
        API.get_bots()*/
        //API.set_wheel_speed("BOT1", .1, .03);
    };

    websocket.onmessage = function (evt) {
        var data = JSON.parse(evt.data);
        if (data.event)
            log_event(data.event);
        log(data, "from-server");
    };
}

function send_command(cmd, args) {
    var cmd = {cmd: cmd};
    if (args) {
        cmd.args = args;
    }
    var msg = JSON.stringify(cmd);
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


function hookToCommandForms() {
    $("form[data-cmd]").each(function(i, elem) {
        var $elem = $(elem);
        $elem.on("submit", function(e) {
            e.preventDefault();
            var cmd = $elem.data("cmd");
            var $fields = $elem.find("input");
            var args = {};
            $fields.each(function(i, e) {
                var $e = $(e);
                var v = $e.val();
                if ($e.attr("type") === "number")
                    v = parseFloat(v);
                args[$e.attr("name")] = v;
            });
            send_command(cmd, args);
        });
    });
}


$(function() {

    connect_to_websocket();
    hookToCommandForms();
});
