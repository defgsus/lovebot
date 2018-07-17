from ..sim import Robot


class LoveUser:

    def __init__(self, server, con, username):
        self.server = server
        self.con = con
        self.username = username
        self.bots = dict()

    def add_bot(self, bot):
        self.bots[bot.bot_id] = bot

    def remove_bot(self, bot_or_botid):
        bot_id = bot_or_botid.bot_id if isinstance(bot_or_botid, Robot) else bot_or_botid
        if bot_id in self.bots:
            del self.bots[bot_id]
