import time
from pyheufybot.utils.fileutils import writeFile

def log(line, path, target=False):
    today = time.strftime("[%H:%M:%S]")
    
    if target:
        print "{} {} - {}".format(today, target, line)
    else:
        print "{} {}".format(today, line)
