import time

def log(line, target):
    today = time.strftime("[%H:%M:%S]")

    if target != None:
        print "{} {} - {}".format(today, target, line)
    else:
        print "{} {}".format(today, line)
    #TODO: Logging to file
