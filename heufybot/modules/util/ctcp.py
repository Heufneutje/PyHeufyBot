from twisted.plugin import IPlugin
from heufybot import __version__
from heufybot.channel import IRCChannel
from heufybot.moduleinterface import BotModule, IBotModule
from heufybot.utils.timeutils import now
from zope.interface import implements
from platform import platform


class CTCP(BotModule):
    implements(IPlugin, IBotModule)

    name = "CTCP"

    def actions(self):
        return [ ("ctcp-message", 1, self.handleCTCP),
                 ("send-ctcp", 1, self.sendCTCPCommand) ]

    def handleCTCP(self, server, source, user, message):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, server):
            return

        if isinstance(source, IRCChannel):
            target = source.name
        else:
            target = source.nick

        if message.upper() == "PING" or message.upper().startswith("PING "):
            self.sendCTCPReply(server, target, "PING", message[5:])
        elif message.upper() == "VERSION":
            self.sendCTCPReply(server, target, "VERSION", "PyHeufyBot v{} / {}".format(__version__, platform()))
        elif message.upper() == "TIME":
            self.sendCTCPReply(server, target, "TIME", str(now()))
        elif message.upper() == "SOURCE":
            self.sendCTCPReply(server, target, "SOURCE", "https://github.com/Heufneutje/PyHeufyBot/")

    def sendCTCPCommand(self, server, target, ctcpType):
        self.bot.servers[server].outputHandler.cmdPRIVMSG(target, "\x01{}\x01".format(ctcpType))

    def sendCTCPReply(self, server, target, ctcpType, reply):
        if reply:
            self.bot.servers[server].outputHandler.cmdNOTICE(target, "\x01{} {}\x01".format(ctcpType, reply))
        else:
            self.bot.servers[server].outputHandler.cmdNOTICE(target, "\x01{}\x01".format(ctcpType))

ctcp = CTCP()
