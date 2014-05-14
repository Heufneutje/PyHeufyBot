Module API documentation
========================

Modules for PyHeufyBot are fairly simple. They have to meet a few requirements to be considered a module. This document will break down what these are and will hopefully help you should you want to create a module yourself.


First of all, every module has to contain a class called `ModuleSpawner`, which inherits from `Module`. If you do not have this, your module will not load.
```python
class ModuleSpawner(Module):
```

Taking a look the `__init__` function, there are six fields that are important.
```python
def __init__(self, bot):
   self.bot = bot
   self.name = "Say"
   self.trigger = "say"
   self.moduleType = ModuleType.COMMAND
   self.messageTypes = ["PRIVMSG"]
   self.helpText = "Usage: say <message> | Makes the bot say the given line"
```

These first ones are simple and probably don’t need more than a simple explanation. `bot` is a reference to the bot instance. You want to have this so your module can interact with it and send messages, for example. `name` is what your module will be referred to as internally. It is also the name that will show up in the help command. Lastly you can specify a `helpText`, which will be displayed when the user calls the help for the module.
```python
self.bot = bot
self.name = "Say"
self.helpText = "Usage: say <message> | Makes the bot say the given line"
```

Next up we have the `trigger` and the `moduleType`. Modules can have three different types:
- Passive: Passive modules will receive every message and perform background tasks like channel logging.
- Trigger: Trigger modules are triggered by certain words said by a user on IRC. The trigger field is important here. The API will perform a regex search on every message and look for this trigger. This trigger can be anywhere in the message
- Command: Command modules are very much like trigger modules, except the trigger has to be at the start of the message and has to be prefixed with the command prefix or the current nickname of the bot. This command prefix can be changed in the configs.
```python
self.trigger = "say"
self.moduleType = ModuleType.COMMAND
```

The last field a module needs to have is the `messageTypes`. These determine what kind of messages the module will trigger on. For these message types IRC commands can be used, as well as numerics.
```python
self.messageTypes = ["PRIVMSG"]
```

That does it for the `__init__` function and the fields. Other than this modules will also have at least three extra functions. Two of these are the `onModuleLoaded` and `onModuleUnloaded` functions. These will trigger automatically when the module is loaded or unloaded by the API. In these functions you can initialize data files and save your persistent data for example.
```python
def onModuleLoaded(self):
def onModuleUnloaded(self):
```

Lastly modules will need an `execute` function. This function is called by the API when a message is received that meets the requirements set in the module’s fields.
```python
def execute(self, message):
    if len(message.params) == 1:
        self.bot.msg(message.replyTo, "Say what?")
    else:
        self.bot.msg(message.replyTo, " ".join(message.params[1:])
```
