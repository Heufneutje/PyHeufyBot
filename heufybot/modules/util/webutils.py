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

    def actions(self):
        return [ ("fetch-url", 1, self.fetchURL),
                 ("post-url", 1, self.postURL),
                 ("post-paste", 1, self.pasteEE),
                 ("shorten-url", 1, self.shortenURL) ]

    def load(self):
        self.timeout = self.bot.config.itemWithDefault("webrequest_timeout", 10)

    def fetchURL(self, url, params = None, extraHeaders = None):
        headers = { "user-agent": "Mozilla/5.0" }
        if extraHeaders:
            headers.update(extraHeaders)
        try:
            request = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            pageType = request.headers["content-type"]
            if not re.match("^(text/.*|application/((rss|atom|rdf)\+)?xml(;.*)?|application/(.*)json(;.*)?)$", pageType):
                # Make sure we don't download any unwanted things
                return None
            log.msg(request.url, level=logging.DEBUG)
            return request
        except (requests.RequestException, requests.ConnectionError) as ex:
            logExceptionTrace("Error while fetching from {}: {}".format(url, ex))
            return None

    def postURL(self, url, data, extraHeaders = None):
        headers = { "user-agent": "Mozilla/5.0" }
        if extraHeaders:
            headers.update(extraHeaders)
        try:
            request = requests.post(url, data=data, headers=headers, timeout=self.timeout)
            pageType = request.headers["content-type"]
            if not re.match("^(text/.*|application/((rss|atom|rdf)\+)?xml(;.*)?|application/(.*)json(;.*)?)$", pageType):
                # Make sure we don't download any unwanted things
                return None
            log.msg(request.url, level=logging.DEBUG)
            return request
        except (requests.RequestException, requests.ConnectionError) as ex:
            logExceptionTrace("Error while posting to {}: {}".format(url, ex))
            return None

    def pasteEE(self, description, data, expiration):
        values = {
            "key": "public",
            "description": description,
            "paste": data,
            "expiration": expiration,
            "format": "json"
        }
        result = self.postURL("http://paste.ee/api", values)
        if not result:
            return None
        json = result.json()
        if json["status"] == "error":
            return "The Paste.ee API returned the following error: {}".format(json["error"])
        elif json["status"] == "success":
            return json["paste"]["link"]
        else:
            return None

    def shortenURL(self, url):
        if url.startswith("http:"):
            j = "{{\"longUrl\": \"{}\"}}".format(url)
        else:
            j = "{{\"longUrl\": \"http://{}/\"\}}".format(url)
        apiURL = "https://www.googleapis.com/urlshortener/v1/url"
        result = self.postURL(apiURL, j, { "Content-Type": "application/json" })
        if not result:
            return None
        json = result.json()
        if "id" not in json:
            return None
        return json["id"]

webutils = WebUtils()
