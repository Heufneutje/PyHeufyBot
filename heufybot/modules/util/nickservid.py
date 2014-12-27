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

        if "nickserv_nick" not in self.bot.config:
            nick = "NickServ"
            self.bot.servers[serverName].log("No valid NickServ nickname was found; defaulting to NickServ...",
                                             level=logging.WARNING)
        else:
            nick = self.bot.config["nickserv_nick"]
        if "nickserv_pass" not in self.bot.config:
            self.bot.servers[serverName].log("No NickServ password found. Aborting authentication...",
                                             level=logging.ERROR)
            return
        password = self.bot.config["nickserv_pass"]
        self.bot.servers[serverName].outputHandler.cmdPRIVMSG(nick, "IDENTIFY {}".format(password))

nickServID = NickServIdentify()
