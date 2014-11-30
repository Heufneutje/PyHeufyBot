from twisted.plugin import IPlugin
from heufybot.moduleinterface import BotModule, IBotModule
from zope.interface import implements
import logging


class NickServIdentify(BotModule):
    implements(IPlugin, IBotModule)

    name = "NickServIdentify"

    def hookBot(self, bot):
        self.bot = bot

    def actions(self):
        return [ ("welcome", 1, self.identify) ]

    def identify(self, serverName):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, serverName):
            return

        nsSettings = self.bot.config.serverItemWithDefault(serverName, self.name, {})
        if "nick" not in nsSettings:
            nick = "NickServ"
            self.bot.servers[serverName].log("No valid NickServ nickname was found; defaulting to NickServ...",
                                             level=logging.WARNING)
        else:
            nick = nsSettings["nick"]
        if "pass" not in nsSettings:
            self.bot.servers[serverName].log("No NickServ password found. Aborting authentication...",
                                             level=logging.ERROR)
            return
        password = nsSettings["pass"]
        self.bot.servers[serverName].outputHandler.cmdPRIVMSG(nick, "IDENTIFY {}".format(password))


nickServID = NickServIdentify()
