from twisted.logger import FileLogObserver, FilteringLogObserver, globalLogPublisher, InvalidLogLevelError, \
    Logger, LogLevel, LogLevelFilterPredicate
from twisted.python.logfile import DailyLogFile
from heufybot.bot import HeufyBot
from heufybot.utils.logutils import consoleLogObserver, logFormat
from signal import signal, SIGINT
import argparse


if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="A modular Twisted IRC bot.")
    parser.add_argument("-c", "--config", help="The configuration file to use", type=str, default="heufybot.yaml")
    parser.add_argument("-f", "--logfile", help="The file the log will be written to", type=str, default="heufybot.log")
    parser.add_argument("-l", "--loglevel", help="The logging level the bot will use", type=str, default="INFO")
    options = parser.parse_args()

    # Start the bot
    heufybot = HeufyBot(options.config)

    # Determine the logging level
    logFilter = LogLevelFilterPredicate()
    try:
        logFilter.setLogLevelForNamespace("heufybot", LogLevel.levelWithName(options.loglevel.lower()))
        invalidLogLevel = False
    except InvalidLogLevelError:
        logFilter.setLogLevelForNamespace("heufybot", LogLevel.info)
        invalidLogLevel = True

    # Set up logging
    logFile = DailyLogFile("heufybot.log", "")
    fileObserver = FileLogObserver(logFile, logFormat)
    fileFilterObserver = FilteringLogObserver(fileObserver, (logFilter,))
    consoleFilterObserver = FilteringLogObserver(consoleLogObserver, (logFilter,))
    heufybot.log = Logger("heufybot")
    globalLogPublisher.addObserver(fileFilterObserver)
    globalLogPublisher.addObserver(consoleFilterObserver)

    heufybot.log.info("Starting bot...")

    # Yell at the user if they specified an invalid log level
    if invalidLogLevel:
        heufybot.log.info("Picked up invalid log level {invalidLevel}, level has been set to INFO instead.",
                          invalidLevel=options.loglevel.lower())
    else:
        heufybot.log.info("Log level has been set to {logLevel}.", logLevel=options.loglevel.upper())

    signal(SIGINT, lambda signal, stack: heufybot.shutdown())
    heufybot.startup()
