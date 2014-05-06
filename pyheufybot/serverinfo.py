class ServerInfo(object):
    def __init__(self):
        self.name = None
        self.version = None
        self.motd = ""
        self.network = "UnknownNetwork"
        
        # Supported modes
        self.userModes = "iosw"
        self.chanModesList = "b"
        self.chanModesParam = "l"
        self.chanModesParamUnset = "k"
        self.chanModesNormal = "imnpst"
        self.prefixesModeToChar = { "o" : "@", "v" : "+" }
        self.prefixesCharToMode = { "@" : "o", "+" : "v" }

        self.chanTypes = "#"

    def appendMotd(self, motdLine):
        self.motd = self.motd + motdLine