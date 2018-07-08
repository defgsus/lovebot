
var websocket = null;
var updateInterval = 100;

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
        API.get_world();
        API.get_bots();
        /*API.get_connections();
        API.create_bot("Viktor");
        API.get_bots()*/
        //API.set_wheel_speed("BOT1", .1, .03);
    };

    websocket.onmessage = function (evt) {
        var data = JSON.parse(evt.data);
        if (data.event)
            log_event(data.event);

        if (data.world) {
            world = data.world;
            paintWorldCanvas();
        }
        else if (data.bots) {
            bots = data.bots;
            paintWorldCanvas();
            setTimeout(function () { API.get_bots(); }, updateInterval);
        }
        else
            log(data, "from-server");
    };
}

function send_command(cmd_name, args) {
    var cmd = {cmd: cmd_name};
    if (args) {
        cmd.args = args;
    }
    var msg = JSON.stringify(cmd);
    if (cmd_name !== "get_bots")
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


var worldBackgroundImage = new Image();
worldBackgroundImage.src = "/worldmap.png";

var world = null;
var bots = null;
var canvas = null;


function paintWorldCanvas() {
    if (!canvas) {
        canvas = document.getElementById("world-canvas").getContext("2d");
    }

    canvas.drawImage(worldBackgroundImage, 0, 0);
    var res_x = worldBackgroundImage.width;
    var res_y = worldBackgroundImage.height;

    if (world && bots) {
        var bbox = world.df.bbox;

        canvas.fillStyle = 'green';
        for (var i in bots) {
            var bot = bots[i];
            var x = (bot.center[0] - bbox.min_x) / (bbox.max_x - bbox.min_x) * res_x;
            var y = res_y - 1 - (bot.center[1] - bbox.min_y) / (bbox.max_y - bbox.min_y) * res_y;
            var r = bot.radius / (bbox.max_y - bbox.min_y) * res_y;
            canvas.beginPath();
            canvas.arc(x, y, r, 0, Math.PI * 2., false);
            canvas.fill();
        }

    }

}

$(function() {

    connect_to_websocket();
    hookToCommandForms();

    $("#update-interval").on("change", function(e) {
        updateInterval = parseInt($("#update-interval").val());
    });
});
