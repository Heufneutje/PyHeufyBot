PyHeufyBot
==========

A rewrite of my Java IRC bot [RE_HeufyBot](https://github.com/Heufneutje/RE_HeufyBot) in Python, using Twisted as its IRC library.

Not much to see here yet as the project is very much a WiP. If you wanna play around with it, do the following:

1. Clone the repository
2. Create a virtualenv and activate it
3. Within the virtualenv, run `pip install -r requirements.txt`. Keep in mind that if you're doing this on Windows, you're going to need the VC9 compiler to build Twisted.
4. Run `python app.py`

Will add more here as time goes on.

RE_HeufyBot's flaws
===================

RE_HeufyBot was an interesting project for me since I didn't use any IRC libraries and had to figure out everything in the core myself. Mainly because it was my first stab at writing things like this, or writing an IRC bot from scratch in general, the project had some fundamental design flaws. The biggest flaws were the broken config files, sockets breaking when trying to reconnect after losing connection, the lack of a message class and the late implementation of multiserver. This last one I regret the most. I should have designed it to be mutliserver in the first place, rather than hacking it into a core based on single connections later. Not having a message class was also quite annoying, as it meant bot instances, server instances and the like were passed around to modules and the code became a mess. Lastly I regret not thinking about how I wanted to do the module API before creating it. In the end I changed it a lot and even after all the changes its possibilties were very limited. This meant channel logging was done in the core, which kinda defeats the purpose of modularity.

Design goals for PyHeufyBot
===========================

- Multiserver. Make the bot connect to multiple servers from the start and build the core to handle these mutliple connections right from the start.
- A well defined module API. I would like the module API to do what RE_HeufyBot's API should have done in the first place; allowing for events to be caught and have the bot execute certain features based on those through its modules.
- A message class. Let every event that happens in the core create an instance of the message class and pass this to the modules. This way no instances of the bot itself or server connections need to be passed.
- Better control over connections. With RE_HeufyBot it was impossible to start any new connections after the config files had been loaded. Reconnecting was impossible as stated before. By making use of Twisted's factories, this should go a lot smoother.

I might add more to this as time goes on, if any more ideas pop into my head.
