from twisted.plugin import IPlugin
from heufybot.moduleinterface import BotModule, IBotModule
from zope.interface import implements


class UserLocationChatmap(BotModule):
    implements(IPlugin, IBotModule)

    name = "UserLocationChatmap"
    baseURL = "http://tsukiakariusagi.net/chatmaplookup.php?"

    def hookBot(self, bot):
        self.bot = bot

    def actions(self):
        return [ ("userlocation", 1, self.userLocationFromDBChatmap) ]

    def userLocationFromDBChatmap(self, server, source, user):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, server):
            return

        params = {
            "nick": user
        }
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", self.baseURL, params)
        if not result:
            self.bot.outputHandler.servers[server].cmdPRIVMSG(source, "Chatmap is currently unavailable. Try again "
                                                                      "later.")
            return None
        if result.text == ",":
            self.bot.outputHandler.servers[server].cmdPRIVMSG(source, "You are not on the chatmap.")
            return {
                "success": False
            }
        else:
            coords = result.text.split(",")
            return {
                "success": True,
                "lat": float(coords[0]),
                "lon": float(coords[1])
            }

userLocDB = UserLocationChatmap()
