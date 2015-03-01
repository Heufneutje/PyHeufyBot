from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements
from random import choice


class ChooseCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Choose"

    def triggers(self):
        return ["choose", "choice"]

    def load(self):
        self.help = "Commands: choose/choice <choice1>, <choice2> | Makes a choice out of the given options at random."
        self.commandHelp = {}

    def execute(self, server, source, command, params, data):
        if len(params) < 1:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Choose what?")
            return
        message = " ".join(params)
        if "," in message:
            options = message.split(",")
        else:
            options = params
        self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Choice: {}".format(choice(options).strip()))

chooseCommand = ChooseCommand()
