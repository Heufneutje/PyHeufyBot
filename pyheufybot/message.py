from pyheufybot.user import IRCUser
from pyheufybot.channel import IRCChannel

class IRCMessage(object):
    def __init__(self, messageType, user, channel, messageText):
        self.messageType = messageType
        self.user = user
        self.channel = channel
        self.messageText = messageText
        
        self.replyTo = ""

        if not user and channel:
            # This message does not have a user or a channel. It's probably a server reply
            self.replyTo = ""
        elif not channel:
            self.replyTo = user.nickname
        else:
            self.replyTo = channel.name