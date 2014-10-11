from twisted.python import log
from heufybot.bot import HeufyBot
from heufybot.utils.logutils import LevelLoggingObserver
import argparse, logging


parser = argparse.ArgumentParser(description="A modular Twisted IRC bot.")
parser.add_argument("-c", "--config", help="The configuration file to use", type=str, default="heufybot.yaml")
parser.add_argument("-f", "--logfile", help="The file the log will be written to", type=str, default="heufybot.log")
parser.add_argument("-l", "--loglevel", help="The logging level the bot will use", type=str, default="INFO")
options = parser.parse_args()

if __name__ == "__main__":
    # Determine the logging level
    numericLevel = getattr(logging, options.loglevel.upper(), None)
    invalidLogLevel = False
    if not isinstance(numericLevel, int):
        numericLevel = logging.INFO
        invalidLogLevel = True

    # Set up logging
    observer = LevelLoggingObserver(open(options.logfile, "a"), numericLevel)
    observer.start()

    # Yell at the user if they specified an invalid log level
    if invalidLogLevel:
        log.msg("Picked up invalid log level {}; defaulting to INFO.".format(options.loglevel), level=logging.WARNING)

    # Start the bot
    heufybot = HeufyBot(options.config)
