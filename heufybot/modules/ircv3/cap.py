from twisted.plugin import IPlugin
from heufybot.moduleinterface import BotModule, IBotModule
from zope.interface import implements


class IRCv3Cap(BotModule):
    implements(IPlugin, IBotModule)

    name = "Cap"
    capabilities = {}

    def actions(self):
        return [ ("prelogin", 1, self.enableCapabilities),
                 ("disconnect", 1, self.clearCapabilities),
                 ("pre-handlecommand-CAP", 1, self.handleCap),
                 ("pre-handlenumeric-401", 1, self.handleNotSupported) ]

    def enableCapabilities(self, server):
        if server in self.capabilities:
            self.bot.log.warn("[{server}] Trying to request capabilities, but capabilities have already been "
                              "requested!")
            return

        self.capabilities[server] = {
            "initializing": True,
            "available": [ "multi-prefix" ], # Enable multi-prefix by default since it's handled in the core
            "requested": [],
            "enabled": []
        }

        caps = []
        self.bot.moduleHandler.runProcessingAction("listcaps", server, caps)
        self.capabilities[server]["available"].extend(caps)
        self.bot.log.info("[{server}] Requesting available capabilities...", server=server)
        self.bot.servers[server].sendMessage("CAP", "LS")

    def clearCapabilities(self, server):
        if server in self.capabilities:
            del self.capabilities[server]

    def handleCap(self, server, nick, ident, host, params):
        if params[1] == "LS":
            self.bot.log.info("[{server}] Received CAP LS reply, server supports capabilities: {caps}.", server=server,
                              caps=params[2])
            serverCaps = _parseCapReply(params[2])
            for reqCap in [x for x in self.capabilities[server]["available"] if x in serverCaps]:
                self.capabilities[server]["requested"].append(reqCap)
            self._checkNegotiationFinished(server)
            if self.capabilities[server]["initializing"]:
                toRequest = " ".join(self.capabilities[server]["requested"])
                self.bot.log.info("[{server}] Requesting capabilities: {caps}...", server=server, caps=toRequest)
                self.bot.servers[server].sendMessage("CAP", "REQ", ":{}".format(toRequest))
        elif params[1] == "ACK" or params[1] == "NAK":
            capList = _parseCapReply(params[2])
            self.capabilities[server]["requested"] = [x for x in self.capabilities[server]["requested"] if x not in
                                                      capList]
            if params[1] == "ACK":
                self.capabilities[server]["enabled"].extend([x for x in capList if x not in self.capabilities[
                    server]["enabled"]])
                self.bot.log.info("[{server}] Acknowledged capability changes: {caps}.", server=server, caps=params[2])
            else:
                self.bot.log.info("[{server}] Rejected capability changes: {caps}.", server=server, caps=params[2])
            self._checkNegotiationFinished(server)

    def handleNotSupported(self, server, prefix, params):
        # This is assuming the numeric is even sent to begin with, which some unsupported IRCds don't even seem to do.
        if params[0] == "CAP":
            self.bot.log.info("[{server}] Server does not support capability negotiation.", server=server)
            self.capabilities[server]["initializing"] = False

    def _checkNegotiationFinished(self, server):
        if len(self.capabilities[server]["requested"]) == 0 and self.capabilities[server]["initializing"]:
            self.bot.servers[server].sendMessage("CAP", "END")
            self.bot.log.info("[{server}] Capability negotiation completed.", server=server)
            self.capabilities[server]["initializing"] = False

def _parseCapReply(reply):
    parsedReply = {}
    for serverCap in reply.split():
        if "=" in serverCap:
            key, value = serverCap.split("=")
        else:
            key = serverCap
            value = None
        parsedReply[key] = value
    return parsedReply


cap = IRCv3Cap()
