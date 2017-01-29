from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class ChatmapCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "DBChatmap"
    chatmapBaseUrl = "https://chatmap.raptorpond.com/"

    def triggers(self):
        return ["chatmap", "addmap", "remmap"]

    def actions(self):
        return super(ChatmapCommand, self).actions() + [ ("userlocation-updated", 1, self.setLocation),
                                                         ("userlocation-deleted", 1, self.deleteLocation) ]

    def load(self):
        self.help = "Commands: chatmap, addmap, remmap | View the Desert Bus Chatmap or add or remove your location to" \
                    " or from it."
        self.commandHelp = {
            "chatmap": "View the Desert Bus Chatmap.",
            "addmap": "Add your location to the Desert Bus Chatmap. Your location needs to already exist in storage.",
            "remmap": "Remove your location from the Desert Bus Chatmap"
        }

        self.apiKey = None
        if "dbchatmap" in self.bot.storage["api-keys"]:
            self.apiKey = self.bot.storage["api-keys"]["dbchatmap"]

    def execute(self, server, source, command, params, data):
        if command == "chatmap":
            self.replyPRIVMSG(server, source, "Desert Bus Chatmap: {}".format(self.chatmapBaseUrl))
            return
        if not self.apiKey:
            self.replyPRIVMSG(server, source, "No Desert Bus Chatmap API key found.")
            return
        if command == "addmap":
            loc = self.bot.moduleHandler.runActionUntilValue("userlocation", server, source, data["user"].nick, True)
            if not loc or not loc["success"]:
                return
            self.replyPRIVMSG(server, source, self.setLocation(data["user"].nick, loc["place"], False))
        elif command == "remmap":
            self.replyPRIVMSG(server, source, self.deleteLocation(data["user"].nick))

    def setLocation(self, nick, location, checkExists = True):
        url = "{}api/chatizen/{}".format(self.chatmapBaseUrl, nick.lower())
        extraHeaders = { "Cookie": "password={}".format(self.apiKey) }
        if checkExists:
            result = self.bot.moduleHandler.runActionUntilValue("fetch-url", url, None, extraHeaders)
            if not result or result.status_code == 404:
                return

        userloc = self.bot.moduleHandler.runActionUntilValue("geolocation-place", location)
        data = "{{ \"lat\": {}, \"lon\": {} }}".format(userloc["latitude"], userloc["longitude"])
        setResult = self.bot.moduleHandler.runActionUntilValue("post-url", url, data, extraHeaders)
        if setResult and setResult.status_code == 204:
            return "Your location has been added to the chatmap."
        else:
            self.bot.log.warn(setResult)
            return "Something went wrong while adding your location to the chatmap."

    def deleteLocation(self, nick):
        url = "{}api/chatizen/{}".format(self.chatmapBaseUrl, nick.lower())
        extraHeaders = {"Cookie": "password={}".format(self.apiKey) }
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", url, None, extraHeaders)
        if not result or result.status_code == 404:
            return "Your location on the chatmap could not be determined."

        deleteResult = self.bot.moduleHandler.runActionUntilValue("delete-url", url, extraHeaders)
        if deleteResult.status_code == 204:
            return "Your location has been removed from the chatmap."
        else:
            self.bot.log.warn(deleteResult)
            return "Something went wrong while removing your location from the chatmap."


chatmapCommand = ChatmapCommand()
