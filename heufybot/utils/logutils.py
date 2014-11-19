from twisted.python import log, util
import logging


class LevelLoggingObserver(log.FileLogObserver):
    def __init__(self, logfile, logLevel):
        log.FileLogObserver.__init__(self, logfile)
        self.logLevel = logLevel

    def __call__(self, eventDict):
        self.emit(eventDict)

    def emit(self, eventDict):
        if eventDict["isError"]:
            level = logging.ERROR
        elif "level" in eventDict:
            level = eventDict["level"]
        else:
            level = logging.INFO
        if level < self.logLevel:
            return

        message = log.textFromEventDict(eventDict)
        if not message:
            return

        logElements = {
            "timestamp": self.formatTime(eventDict["time"]),
            "level": logging.getLevelName(level),
            "system": eventDict["system"],
            "text": message.replace("\n", "\n\t")
        }
        messageString = "{} {}".format(logElements["timestamp"],
                                       log._safeFormat("%(level)7s:[%(system)s]: %(text)s\n", logElements))
        print messageString.replace("\n", "")
        util.untilConcludes(self.write, messageString)
        util.untilConcludes(self.flush)
