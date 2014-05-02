import os, yaml

class Config(object):
    filePath = None

    def __init__(self, filePath):
        self.filePath = filePath
        self.settings = {}

    def loadConfig(self, globalConfig):
        if globalConfig:
            self.settings = globalConfig

        if not os.path.exists(os.path.join("config", self.filePath)):
            print "ERROR: \"{0}\" was not found. Make sure to create it or copy \"{0}.example\" to \"{0}\".".format(self.filePath)
            return False
        else:
            with open(os.path.join("config", self.filePath), 'r') as configFile:
                configData = yaml.load(configFile)

            if configData:
                for key in configData:
                    self.settings[key] = configData[key]
            return True
            
    def getSettingWithDefault(self, setting, defaultValue):
        if setting in self.settings:
            return settings[setting]
        else:
            return defaultValue
