Module API documentation
========================

Modules for PyHeufyBot are fairly simple. They have to meet a few requirements to be considered a module. This document will break down what these are and will hopefully help you should you want to create a module yourself.


First of all, every module has to contain a class called `ModuleSpawner`, which inherits from `Module`. If you do not have this, your module will not load.
```python
class ModuleSpawner(Module):
```

Taking a look the `__init__` function, there are seven fields that are important. Other than that there's a call to the superclass. This is important, because it will pass the bot reference. By calling `self.bot` you can perform things like sending messages.
```python
def __init__(self, bot):
   super(ModuleSpawner, self).__init__(bot)

   self.name = "Say"
   self.trigger = "say"
   self.moduleType = ModuleType.COMMAND
   self.modulePriority = ModulePriority.NORMAL
   self.accessLevel = ModuleAccessType.ANYONE
   self.messageTypes = ["PRIVMSG"]
   self.helpText = "Usage: say <message> | Makes the bot say the given line"
```

These first ones are simple and probably don’t need more than a simple explanation. `name` is what your module will be referred to as internally. It is also the name that will show up in the help command. Lastly you can specify a `helpText`, which will be displayed when the user calls the help for the module.
```python
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

Next up is the `modulePriority` field. The API will sort modules by priority and pass messages to the modules in order from high to low. Modules can also interrupt the passing of the message to lower priority modules. This is explained later.
```python
self.modulePriority = ModulePriority.NORMAL
```

The `accessLevel` field determines who can use the module. This only applies to command modules. Access levels are Anyone and Admins. Admins can be defined in the bot's configs.
```python
self.accessLevel = ModuleAccessType.ANYONE
```

The last field a module needs to have is the `messageTypes`. These determine what kind of messages the module will trigger on. For these message types IRC commands can be used, as well as numerics.
```python
self.messageTypes = ["PRIVMSG"]
```

That does it for the `__init__` function and the fields. Other than this modules will also have at least five extra functions. Two of these are the `onModuleLoaded` and `onModuleUnloaded` functions. These will trigger automatically when the module is loaded or unloaded by the API. In these functions you can initialize data files and save your persistent data for example.
```python
def onModuleLoaded(self):
def onModuleUnloaded(self):
```

There is also the `getHelp` function. This normally returns what is defined in the `helpText`, but you can override it. This is useful when you want to specify help for separate commands within the same modules.
```python
def getHelp(self, command):
```

Data management can be done using the `reloadData` function. This is where you make your module reload its data (from a file from example) should another module call for it. This function is called by the API by means of its `reloadModuleData` function, which takes a list of modules names that should reload their data. 
```python
def reloadData(self):
```

Lastly modules will need an `execute` function. This function is called by the API when a message is received that meets the requirements set in the module’s fields. This function MUST end with a `return True` or `return False`. This will determine whether or not the API should continue passing this message to modules with a lower priority.
```python
def execute(self, message):
    if len(message.params) == 1:
        self.bot.msg(message.replyTo, "Say what?")
    else:
        self.bot.msg(message.replyTo, " ".join(message.params[1:])
```
