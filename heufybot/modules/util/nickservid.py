from twisted.plugin import IPlugin
from heufybot.moduleinterface import BotModule, IBotModule
from zope.interface import implements
import logging


class NickServIdentify(BotModule):
    implements(IPlugin, IBotModule)

    name = "NickServIdentify"

    def actions(self):
        return [ ("welcome", 1, self.identify) ]

    def identify(self, serverName):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, serverName):
            return

        if "nickserv_nick" not in self.bot.config and "nickserv_nick" not in self.bot.config["servers"][serverName]:
            nick = "NickServ"
            self.bot.servers[serverName].log("No valid NickServ nickname was found; defaulting to NickServ...",
                                             level=logging.WARNING)
        else:
            nick = self.bot.config.serverItemWithDefault(serverName, "nickserv_nick", "NickServ")
        if "nickserv_pass" not in self.bot.config and "nickserv_pass" not in self.bot.config["servers"][serverName]:
            self.bot.servers[serverName].log("No NickServ password found. Aborting authentication...",
                                             level=logging.ERROR)
            return
        password = self.bot.config.serverItemWithDefault(serverName, "nickserv_pass", None)
        self.bot.servers[serverName].outputHandler.cmdPRIVMSG(nick, "IDENTIFY {}".format(password))

nickServID = NickServIdentify()
