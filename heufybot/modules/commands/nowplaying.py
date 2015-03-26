# -*- coding: utf-8 -*-
from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils import networkName
from zope.interface import implements
from bs4 import BeautifulSoup


class NowPlayingCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "NowPlaying"

    def triggers(self):
        return ["np", "nplink"]

    def load(self):
        self.help = "Commands: np (<lastfmuser>), nplink <lastfmuser> |  Request your currently playing music (from " \
                    "LastFM) or link your nickname to a LastFM account."
        self.commandHelp = {
            "np": "np (<lastfmuser>) | Request your currently playing music (from LastFM).",
            "nplink": "nplink <lastfmuser> | Link your nickname to your LastFM account."
        }
        if "lastfm-links" not in self.bot.storage:
            self.bot.storage["lastfm-links"] = {}
        self.links = self.bot.storage["lastfm-links"]

    def execute(self, server, source, command, params, data):
        if networkName(self.bot, server) not in self.links:
            self.links[networkName(self.bot, server)] = {}
        if command == "np":
            if len(params) == 0:
                name = data["user"].nick.lower()
            else:
                name = params[0].lower()
            if name in self.links[networkName(self.bot, server)]:
                name = self.links[networkName(self.bot, server)][name]
            url = "http://ws.audioscrobbler.com/1.0/user/{}/recenttracks.rss".format(name)
            result = self.bot.moduleHandler.runActionUntilValue("fetch-url", url)
            if not result:
                m = "No user with the name \"{}\" could be found on LastFM.".format(name)
            else:
                soup = BeautifulSoup(result.text)
                firstItem = soup.find("item")
                if not firstItem:
                    m = "No recently played music was found for user \"{}\"".format(name)
                else:
                    title = firstItem.find("title").text.split(u"–")
                    longLink = firstItem.find("link").text
                    link = self.bot.moduleHandler.runActionUntilValue("shorten-url", longLink)
                    if not link:
                        link = longLink
                    m = "\"{}\" by {} | {}".format(title[1].strip(), title[0].strip(), link)
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)
        elif command == "nplink":
            if len(params) == 0:
                m = "You must provide a LastFM name to link to your nickname."
            else:
                self.links[networkName(self.bot, server)][data["user"].nick.lower()] = params[0].lower()
                self.bot.storage["lastfm-links"] = self.links
                m = "The nickname \"{}\" is now linked to LastFM name \"{}\"".format(data["user"].nick, params[0])
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)

npCommand = NowPlayingCommand()
