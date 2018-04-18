from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements
import random, re


class ApathyCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Apathy"

    def triggers(self):
        return ["insult"]

    def actions(self):
        return super(ApathyCommand, self).actions() + [ ("botmessage", 10, self.beLazy) ]

    def beLazy(self, data):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, data["server"]):
            return
        if random.randint(0, 750) == 0 and len(self.insults) > 0:
            insult = random.choice(self.insults).replace("<nick>", data["user"].nick)
            self.replyPRIVMSG(data["server"], data["source"], insult)
            data.clear()

    def load(self):
        self.help = "Meh."
        self.commandHelp = {}
        if "insult_list" not in self.bot.storage:
            self.bot.storage["insult_list"] = []
        self.insults = self.bot.storage["insult_list"]

    def checkPermissions(self, server, source, user, command):
        return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user,
                                                              "apathy-insults")

    def execute(self, server, source, command, params, data):
        if len(params) < 2:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Insult what?")
            return
        subcommand = params[0].lower()
        if subcommand not in ["add", "remove"]:
            self.replyPRIVMSG(server, source, "Invalid subcommand. Subcommands are add/remove.")
            return
        if subcommand == "add":
            if " ".join(params[1:]).lower() in [x.lower() for x in self.insults]:
                self.replyPRIVMSG(server, source, "I already know that insult...")
                return
            self.insults.append(" ".join(params[1:]))
            self.bot.storage["insult_list"] = self.insults
            self.replyPRIVMSG(server, source, "Alright, I suppose...")
        elif subcommand == "remove":
            regex = re.compile(" ".join(params[1:]), re.IGNORECASE)
            matches = filter(regex.search, self.insults)
            if len(matches) == 0:
                self.replyPRIVMSG(server, source, "I don't even know that insult...")
            elif len(matches) > 1:
                self.replyPRIVMSG(server, source, "That matches way too many insults...")
            else:
                self.insults.remove(matches[0])
                self.bot.storage["insult_list"] = self.insults
                self.replyPRIVMSG(server, source, "Fine, I've forgotten about that one.")


apathy = ApathyCommand()
