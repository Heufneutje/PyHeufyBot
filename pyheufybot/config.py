import os, yaml
from pyheufybot.logger import log

class Config(object):
    def __init__(self, filePath, globalConfig):
        self.filePath = filePath
        if globalConfig:
            self.settings = globalConfig.copy()
        else:
            self.settings = {}

    def loadConfig(self):
        if not os.path.exists(os.path.join("config", self.filePath)):
            log("[Config] ERROR: Config file \"{0}\" was not found. Make sure to create it or copy \"globalconfig.yml.example\" to \"{0}\".".format(self.filePath), None)
            return False
        else:
            with open(os.path.join("config", self.filePath), 'r') as configFile:
                configData = yaml.load(configFile)
            log("[Config] --- Loaded {}.".format(self.filePath), None)

            if configData:
                for key in configData:
                    self.settings[key] = configData[key]
            return True
            
    def getSettingWithDefault(self, setting, defaultValue):
        if setting in self.settings:
            return self.settings[setting]
        else:
            return defaultValue
