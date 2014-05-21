import time
from urllib import urlencode
from urllib2 import build_opener, Request, urlopen, URLError
from urlparse import urlparse

class URLResponse(object):
    def __init__(self, body, domain):
        self.body = body
        self.domain = domain

def fetchURL(url, extraHeaders=None):
    headers = [( "User-agent", "Mozilla/5.0" )]
    if extraHeaders:
        for header in extraHeaders:
            headers.append(extraHeaders)
    try:
        opener = build_opener()
        opener.addheaders = headers
        response = opener.open(url)
        urlResponse = URLResponse(response.read(), urlparse(response.geturl()).hostname)
        return urlResponse
 
    except URLError as e:
        today = time.strftime("[%H:%M:%S]")
        reason = None
        if hasattr(e, "reason"):
            reason = "We failed to reach the server, reason: {}".format(e.reason)
        elif hasattr(e, "code"):
            reason = "The server couldn't fulfill the request, code: {}".format(e.code)
        print "{} *** ERROR: Fetch from \"{} \" failed: {}".format(today, url, reason)

def postURL(url, values, extraHeaders=None):
    headers = { "User-agent" : "Mozilla/5.0" }
    if extraHeaders:
        for header in extraHeaders:
            headers[header] = extraHeaders[header]
    data = urlencode(values)
    try:
        request = Request(url, data, headers)
        response = urlopen(request)
        urlResponse = URLResponse(response.read(), urlparse(response.geturl()).hostname)
        return urlResponse
    except URLError as e:
        today = time.strftime("[%H:%M:%S]")
        reason = None
        if hasattr(e, "reason"):
            reason = "We failed to reach the server, reason: {}".format(e.reason)
        elif hasattr(e, "code"):
            reason = "The server couldn't fulfill the request, code: {}".format(e.code)
        print "{} *** ERROR: Post to \"{} \" failed: {}".format(today, url, reason)
