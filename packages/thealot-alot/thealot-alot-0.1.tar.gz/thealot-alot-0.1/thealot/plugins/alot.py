from .plugin import Plugin

class AlotPlugin(Plugin):

    URL = 'http://hyperboleandahalf.blogspot.co.uk/2010/04/alot-is-better-than-you-at-everything.html'

    help = {
            }

    def hook(self):
        self.bot.hookEvent("pubmsg", self.on_message)

    def unhook(self):
        self.bot.unhookEvent("pubmsg", self.on_message)

    def on_message(self, source=None, target=None, args=None):
        if args.lower().find('alot') != -1:
            self.message(target, "{}: {}".format(source.nick, AlotPlugin.URL))
