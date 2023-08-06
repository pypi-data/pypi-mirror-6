class Plugin:
    """Base class for TheAlot plugins."""
    def __init__(self, bot):
        """
        Create a new insance of the plugin and hook it up to the bot.

        Arguments:
        bot -- instance of TheAlot that the plugin belongs to

        """
        self.bot = bot

        # Add help strings to the "help" command
        if self.help:
            name = self.__module__.split(".")[1]
            self.bot.help[name] = self.help

        self.hook()

    def hook(self):
        """
        Implement this method to hook your methods into IRC events when
        plugin instance is created.

        Example:
            def hook(self):
                self.bot.hookEvent("pubmsg", self.on_message)

        """
        raise NotImplementedError

    def unhook(self):
        """
        Implement this method to unhook your methods from IRC events when
        plugin is destroyed.

        Example:
            def hook(self):
                self.bot.unhookEvent("pubmsg", self.on_message)

        """
        raise NotImplementedError

    def __del__(self):
        """
        Unhook plugin methods from the events and remove help strings
        before destroying the plugin.
        """
        self.unhook()
        name = self.__module__.split(".")[1]
        if name in self.bot.help:
            del self.bot.help[name]

    def notice(self, target, message):
        """Wrapper for the connection.notice() methods."""
        self.bot.connection.notice(target, message)

    def message(self, target, message):
        """Wrapper for the connection.privmsg() methods."""
        self.bot.connection.privmsg(target, message)
