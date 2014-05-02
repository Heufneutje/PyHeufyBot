import os, argparse, site
from pyheufybot.bothandler import BotHandler

parser = argparse.ArgumentParser(description="A modular IRC bot written in Python and Twisted.")
parser.add_argument("-c", "--config", help="the global config file to use (default globalconfig.yml)", type=str, default="globalconfig.yml")
cmdArgs = parser.parse_args()

if __name__ == "__main__":
    # Create folders
    if not os.path.exists(os.path.join("config")):
        os.makedirs("config")
    
    BotHandler(cmdArgs.config)
