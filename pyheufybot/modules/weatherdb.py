import json, os
from pyheufybot.modulehandler import Module, ModuleAccessLevel, ModulePriority, ModuleType
from pyheufybot.utils.fileutils import readFile
from pyheufybot.utils.webutils import fetchURL

class ModuleSpawner(Module):
    baseApiAddress = "http://api.worldweatheronline.com/free/v1/weather.ashx?"
    webAddress = "http://www.worldweatheronline.com/v2/weather.aspx?q="
    chatmapAddress = "http://tsukiakariusagi.net/chatmaplookup.php?nick="

    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "WeatherDB"
        self.trigger = "weather|forecast"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ANYONE
        self.messageTypes = ["PRIVMSG"]
        self.helpText = ""

        self.apiKey = None
        self.apiKeyPath = os.path.join(bot.moduleHandler.dataPath, "keys.json")

    def execute(self, message):
        if "geolocation" not in self.bot.moduleHandler.modules:
            self.bot.msg(message.replyTo, "Module \"GeoLocation\" has to be loaded for this module to work.")
            return True
        if not self.apiKey:
            self.bot.msg(message.replyTo, "API key for WorldWeatherOnline was not found.")
            return True

        if len(message.params) > 2:
            latString = message.params[1]
            lngString = message.params[2]
        else:
            latString = None
            lngString = None

        user = None
        if len(message.params) == 1:
            user = message.user.nickname
        else:
            user = message.params[1]

        url = "{}{}".format(self.chatmapAddress, user)
        print url
        chatmapResult = fetchURL(url)
        if chatmapResult:
            if chatmapResult.body != ", ":
                latString, lngString = chatmapResult.body.split(",", 1)
            else:
                if len(message.params) == 1:
                    self.bot.msg(message.replyTo, "You are not on the chatmap.")
                    return True
        else:
            if len(message.params) == 1:
                    self.bot.msg(message.replyTo, "Chatmap doesn't seem to work right now. Try again later.")
                    return True

        geoLocation = self.bot.moduleHandler.modules["geolocation"]

        try:
            latitude = float(latString)
            longitude = float(lngString)

            result = geoLocation.getGeoLocationFromLatLon(latitude, longitude)
            if result:
                weather = self._getWeather(result[1], result[2])
                if not weather:
                    weather = "No weather could be found for this location."

                self.bot.msg(message.replyTo, "Location: {} | {} | More info: {}{},{}".format(result[0], weather, self.webAddress, result[1], result[2]))
                return True
            else:
                self.bot.msg(message.replyTo, "I don't think that's even a location in this multiverse...")
                return True
        except ValueError:
            pass

        result = geoLocation.getGeoLocationFromPlace(" ".join(message.params[1:]))
        if result:
            weather = self._getWeather(result[1], result[2])
            if not weather:
                weather = "No weather could be found for this location."

            self.bot.msg(message.replyTo, "Location: {} | {} | More info: {}{},{}".format(result[0], weather, self.webAddress, result[1], result[2]))
            return True
        else:
            self.bot.msg(message.replyTo, "I don't think that's even a location in this multiverse...")
            return True

    def onModuleLoaded(self):
        if os.path.exists(self.apiKeyPath):
            try:
                jsonString = readFile(self.apiKeyPath)
                keys = json.loads(jsonString)
                for key in keys:
                    if key["name"] == "worldweatheronline":
                        self.apiKey = key["key"]
            except ValueError:
                # String read is not JSON, use default instead
                pass

    def _getWeather(self, latitude, longitude):
        url = "{}q={},{}&key={}&fx=no&format=json".format(self.baseApiAddress, latitude, longitude, self.apiKey)
        result = fetchURL(url)
        if not result:
            return None
        jsonString = json.loads(fetchURL(url).body)
        return self._parseWeatherJSON(jsonString)

    def _parseWeatherJSON(self, jsonString):
        currentCondition = jsonString["data"]["current_condition"][0]
        tempC = currentCondition["temp_C"]
        tempF = currentCondition["temp_F"]
        weather = currentCondition["weatherDesc"][0]["value"]
        humidity = currentCondition["humidity"]
        windSpeedKmph = currentCondition["windspeedKmph"]
        windSpeedMph = currentCondition["windspeedMiles"]
        windDir = currentCondition["winddir16Point"]

        return "Temp: {}C / {}F | Weather: {} | Humidity: {}% | Wind Speed: {} kmph / {} mph | Wind Direction: {}" \
            .format(tempC, tempF, weather, humidity, windSpeedKmph, windSpeedMph, windDir)
