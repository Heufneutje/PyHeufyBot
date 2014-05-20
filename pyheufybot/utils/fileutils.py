import codecs, os

def readFile(filePath):
    try:
        with open(filePath, "r") as f:
            return f.read()
    except Exception as e:
        print "*** ERROR: An exception occurred while reading file \"{}\" ({})".format(filePath, e)
        return None

def writeFile(filePath, line, append=False):
    try:
        action = "a+" if append else "w"
        with codecs.open(filePath, action, "utf-8") as f:
            f.write(line)
            return True
    except Exception as e:
        print "*** ERROR: An exception occurred while writing file \"{}\" ({})".format(filePath, e)

def createDirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
