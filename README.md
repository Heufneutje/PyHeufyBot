PyHeufyBot [![Ready](https://badge.waffle.io/heufneutje/pyheufybot.svg?label=ready&title=Ready)](https://waffle.io/heufneutje/pyheufybot) [![Updates](https://pyup.io/repos/github/Heufneutje/PyHeufyBot/shield.svg)](https://pyup.io/repos/github/Heufneutje/PyHeufyBot/) [![Python 3](https://pyup.io/repos/github/Heufneutje/PyHeufyBot/python-3-shield.svg)](https://pyup.io/repos/github/Heufneutje/PyHeufyBot/)
==========

A rewrite of my Java IRC bot [RE_HeufyBot](https://github.com/Heufneutje/RE_HeufyBot) in Python, 
using Twisted for its connection management.

If you would like to play around with it, do the following:

1. Clone the repository.
2. Create and activate a virtualenv. You will have to download virtualenv for Python 2 if you do not
already have it. You could also just install the requirements on your machine itself, but a
virtualenv is easier to work with.
3. Once the virtualenv is activated, run `pip install -r requirements.txt`.
4. Create a config file (or copy the example one)  and run `python app.py`.

RE_HeufyBot's flaws
===================

RE_HeufyBot was an interesting project for me since I didn't use any IRC libraries and had to figure
out everything in the core myself. Mainly because it was my first stab at writing things like 
this, or writing an IRC bot from scratch in general, the project had some fundamental design flaws.
The biggest flaws were the broken config files, sockets breaking when trying to reconnect after
losing connection, the lack of a message class and the late implementation of multiserver. This last
one I regret the most. I should have designed it to be mutliserver in the first place, rather than
hacking it into a core based on single connections later. Not having a message class was also quite
annoying, as it meant bot instances, server instances and the like were passed around to modules and
the code became a mess. Lastly I regret not thinking about how I wanted to do the module API before
creating it. In the end I changed it a lot and even after all the changes its possibilties were very
limited. This meant channel logging was done in the core, which kinda defeats the purpose of
modularity.

Design goals for PyHeufyBot
===========================

- Multiserver. Make the bot connect to multiple servers from the start and build the core to handle
  these mutliple connections.
- A well defined module API. I would like the module API to do what RE_HeufyBot's API should have
  done in the first place; allowing for events to be caught and have the bot execute certain 
  features based on those through its modules.
- An action system. This will be the way the core and the modules can communicate with each other
  and also how modules can interact with other modules. This is based on the action system used in
  [txircd](https://github.com/ElementalAlchemist/txircd) and ElementalAlchemist deserves credit for it.
- Better control over connections. With RE_HeufyBot it was impossible to start any new connections 
  after the config files had been loaded. Reconnecting was impossible as stated before. By making 
  use of a Twisted factory, this should go a lot smoother.
