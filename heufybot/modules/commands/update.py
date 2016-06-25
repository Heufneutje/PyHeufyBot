from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements
import os, subprocess, sys


class UpdateCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Update"

    def triggers(self):
        return ["update"]

    def load(self):
        self.help = "Commands: update | Update the bot with the source code from the remote Git repository."
        self.commandHelp = {
            "update": "update | Update the bot to the latest released tag or latest master branch commit."
        }

    def checkPermissions(self, server, source, user, command):
        return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user, "update")

    def execute(self, server, source, command, params, data):
        subprocess.check_call(["git", "checkout", "master"])
        updateChan = self.bot.config.serverItemWithDefault(server, "update_channel", "stable")
        if updateChan not in ["stable", "dev"]:
            self.replyPRIVMSG(server, source, "Invalid update channel. Tell my owner about it.")
            return

        latestTag = None
        if updateChan == "dev":
            subprocess.check_call(["git", "fetch"])
            changes = getChanges("origin/master")
        else:
            subprocess.check_call(["git", "fetch", "--tags"])
            latestTag = subprocess.check_output(["git", "describe", "--abbrev=0", "--tags"])
            changes = getChanges("refs/tags/{}".format(latestTag))

        if len(changes) == 0:
            self.replyPRIVMSG(server, source, "I am already on the latest {} version.".format(updateChan))
            return

        if updateChan == "stable":
            returnCode = subprocess.check_call(["git", "merge"])
        else:
            returnCode = subprocess.check_call(["git", "merge", latestTag])

        if returnCode != 0:
            self.replyPRIVMSG(server, source, "Merge after update failed, please merge manually.")
            return

        try:
            subprocess.check_call([os.path.join(os.path.dirname(sys.executable), "pip"),
                                   "install", "-r", "requirements.txt", "-U"])
        except OSError:
            self.bot.log.warn("[{connection}] pip was not found, requirements were not updated.",
                              connection=server)

        if len(changes) > 10:
            result = self.bot.moduleHandler.runActionUntilValue("post-paste", "Changelog", "\n".join(changes), 10)
            if result:
                changeStr = "Too many commits, list posted here: {}.".format(result)
            else:
                changeStr = "An error occurred while posting the changelog. The PasteEE API seems to be down."
        else:
            changeStr = "New commits: {}.".format(" | ".join(list(reversed(changes))))

        self.replyPRIVMSG(server, source, "Update successful. {}".format(changeStr))


def getChanges(compareLocation):
    output = subprocess.check_output(["git", "log", "--no-merges", "--pretty=format:%s", "..{}".format(
        compareLocation)])
    return [s.strip() for s in output.splitlines()]


updateCommand = UpdateCommand()
