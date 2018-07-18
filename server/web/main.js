
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
    get_users: function () {
        send_command("get_users");
    },
    login: function (name, pw) {
        send_command("login", {name: name, pw: pw});
    },
    create_bot: function (bot_id, name) {
        send_command("create_bot", {bot_id: bot_id, name: name});
    },
    remove_bot: function (bot_id) {
        send_command("remove_bot", {bot_id: bot_id});
    },
    set_wheel_speed: function(bot_id, left, right) {
        send_command("set_wheel_speed", {id: bot_id, speed: [left, right]})
    }
};


function connect_to_websocket() {

    websocket = new WebSocket("ws://{{host}}:{{port}}/ws");

    websocket.onopen = function() {
        API.get_world();
        API.get_bots();
        API.get_users();
    };

    websocket.onclose = function() {
        log_event({ts: 0, name: "lost_connection"});
    };

    websocket.onmessage = function (evt) {
        var data = JSON.parse(evt.data);

        if (data.world) {
            world = data.world;
            paintWorldCanvas();
        }

        if (data.bots) {
            bots = data.bots;
            paintWorldCanvas();
            setTimeout(function () { API.get_bots(); }, updateInterval);
        }

        if (data.event) {
            log_event(data.event);
            API.get_bots();
            API.get_users();
        }

        if (data.users) {
            updateUsersBox(data.users);
        }

        if (!(data.event || data.bots))
            log(data, data.error ? "from-server error" : "from-server");
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

function time_str(seconds) {
    return Math.round(seconds/60/60)+"h"+(Math.round(seconds/60) % 60)+"m"
          +(Math.round(seconds) % 60)+"s";
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
    html += ">"+time_str(ts)+": "+msg+"</div>";
    $(".log-window").prepend($(html));
}

function log_event(event) {
    var msg = JSON.stringify(event.data);
    var html = "<div>"+time_str(event.ts)+": "+event.name+": "+msg+"</div>";
    $(".event-log-window").prepend(html);
}

function updateUsersBox(users) {
    var html = "";
    for (var i in users) {
        var user = users[i];
        html += '<div>' + user.id;
        for (var j in user.bots) {
            var bot_id = user.bots[j];
            var bot = get_bot(bot_id);
            if (bot) {
                html += '<div>'+bot.name+'</div>';
            } else {
                html += '<div>'+bot_id+'</div>';
            }
        }
        html += '</div>';
    }
    $(".users-window").html(html);
}

function get_bot(bot_id) {
    for (var i in bots) {
        if (bots[i].id === bot_id)
            return bots[i];
    }
    return null;
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
        canvas.strokeStyle = 'black';
        canvas.strokeWidth = '3px';
        for (var i in bots) {
            var bot = bots[i];
            var x = (bot.center[0] - bbox.min_x) / (bbox.max_x - bbox.min_x) * res_x;
            var y = res_y - 1 - (bot.center[1] - bbox.min_y) / (bbox.max_y - bbox.min_y) * res_y;
            var r = bot.radius / (bbox.max_y - bbox.min_y) * res_y;
            var head = bot.heading - Math.PI/2.;
            canvas.beginPath();
            canvas.arc(x, y, r, 0, Math.PI * 2., false);
            canvas.fill();

            canvas.beginPath();
            canvas.arc(x, y, r*.9, -0.2+head, 0.2+head, false);
            canvas.arc(x, y, r*.8, -0.2+head, 0.2+head, false);
            canvas.stroke();
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

