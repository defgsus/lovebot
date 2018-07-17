

class LoveApi:

    def __init__(self, send_command_func):
        self.send_command = send_command_func

    def get_bots(self):
        self.send_command("get_bots")

    def get_world(self):
        self.send_command("get_world")

    def get_connections(self):
        self.send_command("get_connections")

    def login(self, username, password):
        self.send_command("login", name=username, pw=password)

    def logout(self):
        self.send_command("logout")

    def create_bot(self, bot_id=None, name=None):
        kwargs = {}
        if bot_id:
            kwargs["bot_id"] = bot_id
        if name:
            kwargs["name"] = name
        self.send_command("create_bot", **kwargs)

    def remove_bot(self, bot_id):
        self.send_command("remove_bot", bot_id=bot_id)

    def set_wheel_speed(self, bot_id, left, right):
        self.send_command("set_wheel_speed", bot_id=bot_id, left=left, right=right)