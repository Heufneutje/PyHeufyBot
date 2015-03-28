from twisted.plugin import IPlugin
from heufybot.channel import IRCChannel
from heufybot.moduleinterface import BotModule, IBotModule
from zope.interface import implements
from bs4 import BeautifulSoup
from urlparse import urlparse
import re


class URLFollow(BotModule):
    implements(IPlugin, IBotModule)

    name = "URLFollow"

    def actions(self):
        return [ ("ctcp-message", 1, self.searchActions),
                 ("message-channel", 1, self.searchChannelMessage),
                 ("message-user", 1, self.searchPrivateMessage) ]

    def searchPrivateMessage(self, server, user, messageBody):
        self._searchURLs(server, user.nick, messageBody)

    def searchChannelMessage(self, server, channel, user, body):
        self._searchURLs(server, channel.name, body)

    def searchActions(self, server, source, user, body):
        if not body.upper().startswith("ACTION"):
            return
        if isinstance(source, IRCChannel):
            self._searchURLs(server, source.name, body)
        else:
            self._searchURLs(server, user.nick, body)

    def _searchURLs(self, server, source, body):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, server):
            return
        regex = re.compile(r"(https?://|www\.)[^\s]+", re.IGNORECASE)
        for url in filter(regex.match, body.split(" ")):
            response = self._handleURL(url)
            if response:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, response)

    def _handleURL(self, url):
        # Work in progress
        # ytMatch = re.search(r"(youtube\.com/watch.+v=|youtu\.be/)(?P<videoID>[^&#\?]{11})", url)
        # if ytMatch:
        #     return self._handleYouTube(ytMatch.group("videoID"))
         #imgurMatch = re.search(r"(i\.)?imgur\.com/(?P<imgurID>[^\.]+)", url)
        # if imgurMatch:
        #     return self._handleImgur(imgurMatch.group("imgurID"))
        if not re.search("\.(jpe?g|gif|png|bmp)$", url):
            return self._handleGeneric(url)
        return None

    def _handleGeneric(self, url):
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", url)
        if not result or result.status_code != 200:
            return None
        parsed_uri = urlparse(result.url)
        soup = BeautifulSoup(result.content)
        title = soup.find("title").text.encode("utf-8", "ignore").replace("\r", "").replace("\n", " ")
        if len(title) > 300:
            title = title[:297] + "..."
        return "[Standard URL] Title: {} (at host: {}).".format(title, parsed_uri.hostname)

    def _handleYouTube(self, videoID):
        pass

    def _handleImgur(self, imgurID):
        pass

urlFollow = URLFollow()
