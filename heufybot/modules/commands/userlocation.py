from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils import networkName
from zope.interface import implements
import json, os.path


class UserLocation(BotCommand):
    implements(IPlugin, IBotModule)

    name = "UserLocation"

    def triggers(self):
        return ["addloc", "remloc", "locimport", "locexport"]

    def actions(self):
        return super(UserLocation, self).actions() + [ ("userlocation", 1, self.lookUpLocation) ]

    def lookUpLocation(self, server, source, user, displayErrors):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, server):
            return

        if networkName(self.bot, server) in self.locations and user.lower() in self.locations[networkName(self.bot,
                                                                                                          server)]:
            return {
                "success": True,
                "place": self.locations[networkName(self.bot, server)][user.lower()]
            }
        if displayErrors:
            error = "Your location is not registered. Register your location by using the \"addloc\" command or " \
                    "provide a location."
            self.replyPRIVMSG(server, source, error)
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

    def checkPermissions(self, server, source, user, command):
        if command == "locimport" or command == "locexport":
            return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user,
                                                                  "location-import-export")
        return True

    def execute(self, server, source, command, params, data):
        if command == "addloc":
            if len(params) < 1:
                self.replyPRIVMSG(server, source, "What do you want to do with your location?")
                return
            if networkName(self.bot, server) not in self.locations:
                self.locations[networkName(self.bot, server)] = {}
            self.locations[networkName(self.bot, server)][data["user"].nick.lower()] = " ".join(params)
            self.bot.storage["userlocations"] = self.locations
            self.bot.moduleHandler.runGenericAction("userlocation-updated", data["user"].nick, " ".join(params))
            self.replyPRIVMSG(server, source, "Your location has been updated.")
        elif command == "remloc":
            if data["user"].nick.lower() not in self.locations[networkName(self.bot, server)]:
                self.replyPRIVMSG(server, source, "Your location is not registered!")
            else:
                del self.locations[networkName(self.bot, server)][data["user"].nick.lower()]
                self.bot.storage["userlocations"] = self.locations
                self.bot.moduleHandler.runGenericAction("userlocation-deleted", data["user"].nick)
                self.replyPRIVMSG(server, source, "Your location has been removed.")
        elif command == "locimport":
            if len(params) < 1:
                self.replyPRIVMSG(server, source, "Import locations from where?")
                return
            if not os.path.isfile(params[0]):
                self.replyPRIVMSG(server, source, "Import file doesn't exist.")
                return
            with open(params[0]) as importFile:
                try:
                    j = json.load(importFile)
                except ValueError as e:
                    self.replyPRIVMSG(server, source, "An error occurred while reading the import file: {0}.".format(e))
                    return
            if networkName(self.bot, server) not in self.locations:
                self.locations[networkName(self.bot, server)] = {}
            skipped = 0
            for nick, location in j.iteritems():
                if nick in self.locations[networkName(self.bot, server)]:
                    skipped += 1
                    continue
                self.locations[networkName(self.bot, server)][nick] = location
            self.bot.storage["userlocations"] = self.locations
            if skipped == 0:
                msg = "Imported {} location(s).".format(len(j))
            else:
                msg = "Imported {} location(s). Skipped {} location(s) because of a nickname conflict." \
                    .format(len(j) - skipped, skipped)
            self.replyPRIVMSG(server, source, msg)
        elif command == "locexport":
            if len(params) < 1:
                self.replyPRIVMSG(server, source, "Export locations to where?")
                return
            with open(params[0], "w") as exportFile:
                if networkName(self.bot, server) not in self.locations:
                    self.replyPRIVMSG(server, source, "No locations to export.")
                    return
                locations = self.locations[networkName(self.bot, server)]
                json.dump(locations, exportFile, sort_keys=True, indent=4)
                self.replyPRIVMSG(server, source, "Exported {} location(s).".format(len(locations)))


userLocStorage = UserLocation()
