from enum import Enum

class ServerInfo(object):
    def __init__(self):
        self.name = None
        self.version = None
        self.motd = ""
        self.network = "UnknownNetwork"
        self.chanTypes = "#"

        # Supported usermodes. These will most likely be overwritten unless the server has USERMODES in 005
        self.userModes = {}
        self.userModes["i"] = ModeType.NORMAL
        self.userModes["o"] = ModeType.NORMAL
        self.userModes["s"] = ModeType.LIST
        self.userModes["w"] = ModeType.NORMAL

        # Supported channel modes
        self.chanModes = {}
        self.chanModes["b"] = ModeType.LIST
        self.chanModes["i"] = ModeType.NORMAL
        self.chanModes["k"] = ModeType.PARAM_SETUNSET
        self.chanModes["l"] = ModeType.PARAM_SET
        self.chanModes["m"] = ModeType.NORMAL
        self.chanModes["n"] = ModeType.NORMAL
        self.chanModes["p"] = ModeType.NORMAL
        self.chanModes["s"] = ModeType.NORMAL
        self.chanModes["t"] = ModeType.NORMAL

        # Supported status modes
        self.prefixesModeToChar = {}
        self.prefixesModeToChar["o"] = "@"
        self.prefixesModeToChar["v"] = "+"

        self.prefixesCharToMode = {}
        self.prefixesCharToMode["@"] = "o"
        self.prefixesCharToMode["+"] = "v"

        self.prefixOrder = "ov"

    def appendMotd(self, motdLine):
        self.motd = self.motd + motdLine

    def getChanModeType(self, mode):
        if mode in self.chanModes:
            return self.chanModes[mode]
        else:
            return None

class ModeType(Enum):
    LIST = 1
    PARAM_SET = 2
    PARAM_SETUNSET = 3
    NORMAL = 4
