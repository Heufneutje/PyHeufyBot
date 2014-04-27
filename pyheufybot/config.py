import os, yaml

class Config(object):
    filePath = None

    def __init__(self, filePath):
        self.filePath = filePath
        self.settings = {}

    def loadConfig(self, globalConfig):
        if globalConfig:
            self.settings = globalConfig

        print os.path.join("config", self.filePath)

        if not os.path.exists(os.path.join("config", self.filePath)):
            self.createDefaultConfig(os.path.join("config", self.filePath))
        else:
            with open(self.filePath, 'r') as configFile:
                configData = yaml.load(configFile)

            if configData:
                for key in configData:
                    self.settings[key] = configData[key]

    def createDefaultConfig(self, filePath):
        self.settings["nickname"] = "PyHeufyBot"
        self.settings["username"] = "PyHeufyBot"
        self.settings["realname"] = "PyHeufyBot"
        self.settings["server"] = "irc.example.com"
        self.settings["port"] = 6667
        self.settings["channels"] = []

        with open(filePath, 'w') as configFile:
            configData = yaml.dump(self.settings, configFile)
    
    def getSettingWithDefault(self, setting, defaultValue):
        if setting in self.settings:
            return settings[setting]
        else:
            return defaultValue