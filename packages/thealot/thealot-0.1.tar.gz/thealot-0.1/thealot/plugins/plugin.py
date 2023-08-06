class Plugin:

    def __init__(self, bot):
        self.bot = bot
        if self.help:
            name = self.__module__.split(".")[1]
            self.bot.help[name] = self.help
        self.hook()

    def __del__(self):
        self.unhook()

    def notice(self, target, message):
        self.bot.connection.notice(target, message)

    def message(self, target, message):
        self.bot.connection.privmsg(target, message)
