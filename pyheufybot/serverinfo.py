from enum import Enum

class ServerInfo(object):
    def __init__(self):
        self.name = None
        self.version = None
        self.network = "UnknownNetwork"
        self.chanTypes = "#"

        # Supported usermodes
        self.userModes = {"i": ModeType.NORMAL, "o": ModeType.NORMAL, "s": ModeType.LIST, "w": ModeType.NORMAL}

        # Supported channel modes
        self.chanModes = {"b": ModeType.LIST, "i": ModeType.NORMAL, "k": ModeType.PARAM_SETUNSET,
                          "l": ModeType.PARAM_SET, "m": ModeType.NORMAL, "n": ModeType.NORMAL, "p": ModeType.NORMAL,
                          "s": ModeType.NORMAL, "t": ModeType.NORMAL}

        # Supported status modes
        self.prefixesModeToChar = {"o": "@", "v": "+"}
        self.prefixesCharToMode = {"@": "o", "+": "v"}
        self.prefixOrder = "ov"

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
