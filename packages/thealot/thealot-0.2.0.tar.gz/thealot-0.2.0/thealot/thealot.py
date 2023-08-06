"""
The Alot
========

Modular IRC bot for Python.

"""
import importlib
import json
import irc.bot
import irc.strings
from imp import reload
import sys
import os
import thealot.plugins
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.getcwd()

def to_camel_case(s):
    """Convert given underscore string into CammelCase and return it.

    Example:
    some_plugin -> SomePlugin

    """
    if s.__contains__("_"):
        out = ""
        for part in s.split("_"):
            out += part.title()
        return out
    else:
        return s.title()

def print_stack():
    """Print the stack trace of the currently handled exception to the standard output."""
    import traceback
    e = sys.exc_info()
    print(e)
    traceback.print_tb(e[2])

class TheAlot(irc.bot.SingleServerIRCBot):
    """A modular single-chanel IRC bot."""
    def __init__(self, config='config.json'):
        """Create and configure a new instance of the bot.

        Keyword arguments:
        config -- a json configuration file to use (default config.json)

        """
        self.configFile = os.path.join(BASE_DIR, config)

        print("Loading configuration from {}".format(self.configFile))
        with open(self.configFile, 'r') as fh:
            self.config = json.load(fh)

        engine = create_engine(self.config['database'])
        Session = sessionmaker(bind=engine)
        self.db = Session()

        irc.bot.SingleServerIRCBot.__init__(self, 
            [(self.config['server'], self.config['port'])],
            self.config['nickname'],
            self.config['nickname']
        )

        self.connection.buffer_class.errors = 'replace' # Stop clients with latin-1 from crashing the bot

        self.hooks = {
                "pubmsg" : [],
                "welcome" : []
                }
        self.help = {"list" : "Display list of commands"}
        self.initCommands()
        self.initPlugins()

    def __del__(self):
        """Close the database connection when this bot instance is destroyed."""
        try:
            self.db.close()
        except:
            pass

    def hookEvent(self, eventType, method):
        """Add an event hook.

        Arguments: 
        eventType -- type of event (See self.hooks for acceptable types)
        method -- method to call on event

        """
        self.hooks[eventType].append(method)

    def unhookEvent(self, eventType, method):
        """Silently attempt to remove event hook from specified event.

        Arguments:
        eventType -- type of event (See self.hooks for accepted types)
        method -- method to remove

        """
        if method in self.hooks[eventType]:
            self.hooks[eventType].remove(method)

    def initPlugins(self):
        """Load plugins listed in the config and add them to the plugin list."""
        self.plugins = {}
        if "plugins" in self.config:
            for plugin in self.config['plugins']:
                self.loadPlugin(plugin=plugin)
        else:
            self.config['plugins'] = {}

    def initCommands(self):
        """Add core commands to the command list."""
        self.commands = {
                'help' : self.showHelp,
                'list' : self.listCommands,
                'load' : self.loadPlugin,
                'unload' : self.unloadPlugin,
                }

    def loadPlugin(self, source=None, target=None, plugin=None):
        """Load a plugin.

        Import the plugin from plugins namespace, initialise and add it to the plugin list.
        If plugin is already loaded it is first unloaded.

        Keyword arguments:
        source -- 
        target --
        plugin -- underscore name of the plugin to be loaded without the trailing \"Plugin\" (default None)

        Example:
        To load SomeFancyPlugin pass \"some_fancy\" to this method.

        """
        if plugin in self.plugins:
            self.unloadPlugin(plugin=plugin)

        try:
            print(plugin)
            name = to_camel_case(plugin) + "Plugin"
            module = __import__("thealot.plugins."+plugin, fromlist=[name])
            module = reload(module)
            print("Loading {}".format(name))
            self.plugins[plugin] = getattr(module, name)(self)
        except Exception as e:
            print_stack()
            print(e)

    def unloadPlugin(self, source=None, target=None, plugin=None):
        """Attempt to silently unload a plugin.

        Keyword arguments:
        source --
        target -- 
        plugin -- underscore name of the plugin that was used to load it with TheAlot.loadPlugin() (default None)

        """
        if plugin in self.plugins:
            self.plugins[plugin].__del__()
            del self.plugins[plugin]

    def showHelp(self, source=None, target=None, cmd=None):
        """Display help to the user.

        Display usage instructions if no command is given otherwise display help for the given command or an error.

        Keyword arguments:
        source -- channel or user query that the request came from (default None)
        target --
        cmd -- display help for this command and all of its subcommands

        """
        if not cmd:
            self.connection.notice(source, "Usage: help <command>")
        elif cmd in self.help:
            for subcmd in self.help[cmd]:
                # dynamically adjust for the longest key in help
                self.connection.notice(source, "{:<30} {}".format(subcmd, self.help[cmd][subcmd]))
        else:
            self.connection.notice(source, "No help for that command")

    def listCommands(self, source=None, target=None, args=None):
        """Display a list of all currently active commands."""
        for cmd in self.commands:
            self.connection.notice(source, cmd)

    def saveConfig(self, source=None, args=None):
        """Save the configuration to a file."""
        print(self.config)
        fh = open(self.configFile, "w")
        fh.write(json.dumps(self.config, indent=" "*4))
        fh.close()


    def on_nicknameinuse(self, c, e):
        """Override the method to append an underscore to the nick if current nick is already in use."""
        print("Nick in use, appending _")
        c.nick(c.get_nickname() + "_")

    def callbacks(self, eventType, source, target, args):
        """Call all of the hooked methods for a given event.

        Arguments:
        eventType -- type of event (See self.hooks for acceptable types)
        source -- 
        target --
        args --

        """
        for callback in self.hooks[eventType]:
            try:
                callback(source, target, args)
            except:
                print_stack()

    def on_welcome(self, c, e):
        """Override the method to call the \"welcome\" hooks.

        Arguments:
        c --
        e --

        """
        self.callbacks('welcome', e.source, e.target, e.arguments[0])
        c.join(self.config['channel'])

    def on_privmsg(self, c, e):
        """Override the method parse private messages for commands."""
        msg = e.arguments[0]
        if msg[0] != self.config['prefix']:
            msg = self.config['prefix'] + msg
        self.callbacks('pubmsg', e.source, e.target, msg)
        self.parse_user_command(e.source, e.target, msg)

    def on_pubmsg(self, c, e):
        """Override the method parse public messages for commands."""
        self.callbacks('pubmsg', e.source, e.target, e.arguments[0])
        self.parse_user_command(e.source, e.target, e.arguments[0])

    def parse_user_command(self, source, target, msg):
        """Check if message starts with command prefix and attempt to call appropriate command."""
        if msg[0] == self.config['prefix']:
            command = msg[1:].split(" ", 1)
            command[0] = command[0].lower()
            if command[0] in self.commands:
                try:
                    if len(command) == 2:
                        self.commands[command[0]](source, target, command[1])
                    else:
                        self.commands[command[0]](source, target)
                except:
                    print_stack()
            else:
               self.connection.privmsg(source, "Invalid Command")

def main():
    # TODO allow passing config path as argument
    alot = TheAlot()
    alot.start()

if __name__ == "__main__":
    main()

