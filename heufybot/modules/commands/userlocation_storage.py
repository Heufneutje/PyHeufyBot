from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils import networkName
from zope.interface import implements


class UserLocationStorage(BotCommand):
    implements(IPlugin, IBotModule)

    name = "UserLocationStorage"

    def triggers(self):
        return ["addloc", "remloc"]

    def actions(self):
        return super(UserLocationStorage, self).actions() + [
            ("userlocation", 1, self.lookUpLocation) ]

    def lookUpLocation(self, server, source, user, displayErrors):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, server):
            return

        if networkName(self.bot, server) in self.locations and user.lower() in self.locations[networkName(self.bot, \
                server)]:
            return {
                "success": True,
                "place": self.locations[networkName(self.bot, server)][user.lower()]
            }
        if displayErrors:
            error =  "Your location is not registered. Register your location by using the \"addloc\" command or by " \
                     "providing a location."
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, error)
            return {
                "success": False
            }

    def load(self):
        self.help = "Commands: addloc <location>, remloc | Adds or removes your location to the bot's location storage."
        self.commandHelp = {
            "addloc": "addloc <location> | Add your location to the location storage.",
            "remloc": "remloc | Remove your location from the location storage."
        }
        if "userlocations" not in self.bot.storage:
            self.bot.storage["userlocations"] = {}
        self.locations = self.bot.storage["userlocations"]

    def execute(self, server, source, command, params, data):
        if command == "addloc":
            if len(params) < 1:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "What do you want to do with your location?")
                return
            if networkName(self.bot, server) not in self.locations:
                self.locations[networkName(self.bot, server)] = {}
            self.locations[networkName(self.bot, server)][data["user"].nick.lower()] = " ".join(params)
            self.bot.storage["userlocations"] = self.locations
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Your location has been updated.")
        elif command == "remloc":
            if data["user"].nick.lower() not in self.locations[networkName(self.bot, server)]:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Your location is not registered!")
            else:
                del self.locations[networkName(self.bot, server)][data["user"].nick.lower()]
                self.bot.storage["userlocations"] = self.locations
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Your location has been removed.")

userLocStorage = UserLocationStorage()
