from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils import networkName
from zope.interface import implements


class NowPlayingCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "NowPlaying"

    def triggers(self):
        return ["np", "nplink"]

    def load(self):
        self.help = "Commands: np (<lastfmuser>), nplink <lastfmuser> | Request your currently playing music (from " \
                    "LastFM) or link your nickname to a LastFM account."
        self.commandHelp = {
            "np": "np (<lastfmuser>) | Request your currently playing music (from LastFM).",
            "nplink": "nplink <lastfmuser> | Link your nickname to your LastFM account."
        }
        if "lastfm-links" not in self.bot.storage:
            self.bot.storage["lastfm-links"] = {}
        self.links = self.bot.storage["lastfm-links"]
        self.lastfmKey = None
        if "lastfm" in self.bot.storage["api-keys"]:
            self.lastfmKey = self.bot.storage["api-keys"]["lastfm"]

    def execute(self, server, source, command, params, data):
        if not self.lastfmKey:
            self.replyPRIVMSG(server, source, "No LastFM API key was found.")
            return

        if networkName(self.bot, server) not in self.links:
            self.links[networkName(self.bot, server)] = {}
        if command == "np":
            if len(params) == 0:
                name = data["user"].nick.lower()
            else:
                name = params[0].lower()
            if name in self.links[networkName(self.bot, server)]:
                name = self.links[networkName(self.bot, server)][name]
            url = "http://ws.audioscrobbler.com/2.0/"
            params = {
                "method": "user.getrecenttracks",
                "limit": "1",
                "format": "json",
                "user": name,
                "api_key": self.lastfmKey
            }
            result = self.bot.moduleHandler.runActionUntilValue("fetch-url", url, params)
            if not result:
                m = "An error occurred while retrieving data from LastFM."
            else:
                j = result.json()
                if "error" in j and j["error"] == 6:
                    m = "No user with the name {!r} could be found on LastFM.".format(name)
                elif len(j["recenttracks"]["track"]) == 0:
                    m = "No recently played music was found for user {!r}".format(name)
                else:
                    track = j["recenttracks"]["track"][0]
                    artist = track["artist"]["#text"].encode("utf-8", "ignore")
                    songTitle = track["name"].encode("utf-8", "ignore")
                    longLink = track["url"]
                    link = self.bot.moduleHandler.runActionUntilValue("shorten-url", longLink)
                    if not link:
                        link = longLink
                    m = "'{}' by {} | {}".format(songTitle, artist, link)
            self.replyPRIVMSG(server, source, m)
        elif command == "nplink":
            if len(params) == 0:
                m = "You must provide a LastFM name to link to your nickname."
            else:
                self.links[networkName(self.bot, server)][data["user"].nick.lower()] = params[0].lower()
                self.bot.storage["lastfm-links"] = self.links
                m = "The nickname {!r} is now linked to LastFM name {!r}".format(data["user"].nick, params[0])
            self.replyPRIVMSG(server, source, m)


npCommand = NowPlayingCommand()
