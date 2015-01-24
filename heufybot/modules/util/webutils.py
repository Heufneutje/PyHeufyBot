from twisted.plugin import IPlugin
from heufybot.moduleinterface import BotModule, IBotModule
from heufybot.utils.logutils import logExceptionTrace
from zope.interface import implements
import re, requests


class WebUtils(BotModule):
    implements(IPlugin, IBotModule)

    name = "WebUtils"
    canDisable = False

    def hookBot(self, bot):
        self.bot = bot

    def actions(self):
        return [ ("fetch-url", 1, self.fetchURL) ]

    def fetchURL(self, url, params = None):
        try:
            request = requests.get(url, params=params)
            pageType = request.headers["content-type"]
            if not re.match("^(text/.*|application/((rss|atom|rdf)\+)?xml(;.*)?|application/(.*)json(;.*)?)$", pageType):
                # Make sure we don't download any unwanted things
                return None

            return request
        except Exception as ex:
            logExceptionTrace("Error while fetching from {}: {}".format(url, ex))
            return None

webutils = WebUtils()
