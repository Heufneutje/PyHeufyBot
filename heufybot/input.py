from twisted.words.protocols import irc


class InputHandler(object):
    def __init__(self, connection):
        self.connection = connection

    def handleCommand(self, command, prefix, params):
        if command == irc.RPL_WELCOME:
            self.connection.loggedIn = True
