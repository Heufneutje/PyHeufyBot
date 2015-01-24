from twisted.plugin import IPlugin
from twisted.python import log
from heufybot.moduleinterface import BotModule, IBotModule
from heufybot.utils.logutils import logExceptionTrace
from zope.interface import implements
import logging, re, requests


class WebUtils(BotModule):
    implements(IPlugin, IBotModule)

    name = "WebUtils"
    canDisable = False

    def hookBot(self, bot):
        self.bot = bot

    def actions(self):
        return [ ("fetch-url", 1, self.fetchURL) ]

    def fetchURL(self, url, params = None, extraHeaders = None):
        headers = { "user-agent": "Mozilla/5.0" }
        if extraHeaders:
            headers.update(extraHeaders)
        try:
            request = requests.get(url, params=params, headers=headers)
            pageType = request.headers["content-type"]
            if not re.match("^(text/.*|application/((rss|atom|rdf)\+)?xml(;.*)?|application/(.*)json(;.*)?)$", pageType):
                # Make sure we don't download any unwanted things
                return None
            log.msg(request.url, level=logging.DEBUG)
            return request
        except requests.RequestException as ex:
            logExceptionTrace("Error while fetching from {}: {}".format(url, ex))
            return None

webutils = WebUtils()
