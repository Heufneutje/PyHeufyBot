import yaml

class Config(object):
    filePath = None

    def __init__(self, filePath):
        self.filePath = filePath

    def loadConfig(self):
        pass
    
    def getSettingWithDefault(self, default):
        pass