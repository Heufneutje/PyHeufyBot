class CapHandler(object):
    def __init__(self, bot):
        self.bot = bot 
        self.availableCaps = []
        self.enabledCaps = []
        self.finishedCaps = []
        self.capEndSent = False

    def checkFinishedCaps(self):
        if len(self.enabledCaps) == len(self.finishedCaps):
            self.bot.sendLine("CAP END")
            self.capEndSent = True

    def resetCaps(self):
        self.availableCaps.clear()
        self.finishedCaps.clear()
        self.capEndSent = False
