from enum import Enum

class IRCMessage(object):
    def __init__(self, messageType, user, channel, messageText, serverInfo):
        self.messageType = messageType
        self.user = user
        self.channel = channel
        self.messageText = messageText
        self.serverInfo = serverInfo
        self.params = messageText.split(" ")
        
        self.replyTo = ""

        if not user and not channel:
            # This message does not have a user or a channel. It's probably a server reply
            self.replyTo = ""
        elif not channel:
            self.replyTo = user.nickname
        else:
            self.replyTo = channel.name

class IRCResponse(object):
    def __init__(self, target, responseText, responseType):
        self.target = target
        self.responseType = responseType
        self.responseText = responseText

class ResponseType(Enum):
    MESSAGE = 1
    ACTION = 2
    NOTICE = 3
    RAW = 4
