class CapHandler(object):
    def __init__(self, bot):
        self.bot = bot
        self.availableCaps = []
        self.enabledCaps = []
        self.finishedCaps = []

    def checkFinishedCaps(self):
        if enabledCaps.keys.issubset(self.finishedCaps):
            self.bot.sendLine("CAP END")
