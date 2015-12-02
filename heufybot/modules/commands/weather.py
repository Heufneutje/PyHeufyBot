# -*- coding: utf-8 -*-
from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils.timeutils import now, timestamp
from zope.interface import implements
from datetime import datetime


class WeatherCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Weather"
    weatherBaseURL = "http://api.openweathermap.org/data/2.5/weather?"
    forecastBastURL = "http://api.openweathermap.org/data/2.5/forecast/daily?"

    def triggers(self):
        return ["weather", "forecast"]

    def load(self):
        self.help = "Commands: weather <lat> <lon>, weather <place>, weather <nickname>, forecast <lat> <lon>, " \
                    "forecast <place>, forecast <nickname> | Get the current weather conditions or forecast for the " \
                    "given latlon, place or user."
        self.commandHelp = {
            "weather": "weather <lat> <lon>, weather <place>, weather <nickname> | Get the current weather condidions "
                       "for the given latlon, place or user.",
            "forecast": "forecast <lat> <lon>, forecast <place>, forecast <nickname> | Get the forecast for the given "
                        "latlon, place or user."
        }
        self.apiKey = None
        if "openweathermap" in self.bot.storage["api-keys"]:
            self.apiKey = self.bot.storage["api-keys"]["openweathermap"]

    def execute(self, server, source, command, params, data):
        if not self.apiKey:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "No API key found.")
            return

        # Use the user's nickname as a parameter if none were given
        if len(params) == 0:
            params.append(data["user"].nick)
            selfSearch = True
        else:
            selfSearch = False

        # Try using latlon to get the location
        try:
            lat = float(params[0])
            lon = float(params[1])
            location = self.bot.moduleHandler.runActionUntilValue("geolocation-latlon", lat, lon)
            if not location:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I can't determine locations at the moment. "
                                                                          "Try again later.")
                return
            if not location["success"]:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I don't think that's even a location in "
                                                                          "this multiverse...")
                return
            self._handleCommandWithLocation(server, source, command, location)
            return
        except (IndexError, ValueError):
            pass # The user did not give a latlon, so continue using other methods

        # Try to determine the user's location from a nickname
        if self.bot.config.serverItemWithDefault(server, "use_userlocation", False):
            userLoc = self.bot.moduleHandler.runActionUntilValue("userlocation", server, source, params[0], selfSearch)
            if selfSearch:
                if not userLoc:
                    return
                elif not userLoc["success"]:
                    return
            if userLoc and userLoc["success"]:
                if "lat" in userLoc:
                    location = self.bot.moduleHandler.runActionUntilValue("geolocation-latlon", userLoc["lat"],
                                                                          userLoc["lon"])
                else:
                    location = self.bot.moduleHandler.runActionUntilValue("geolocation-place", userLoc["place"])
                if not location:
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I can't determine locations at the "
                                                                              "moment. Try again later.")
                    return
                if not location["success"]:
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I don't think that's even a location in "
                                                                              "this multiverse...")
                    return
                self._handleCommandWithLocation(server, source, command, location)
                return

        # Try to determine the location by the name of the place
        location = self.bot.moduleHandler.runActionUntilValue("geolocation-place", " ".join(params))
        if not location:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I can't determine locations at the moment. "
                                                                      "Try again later.")
            return
        if not location["success"]:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I don't think that's even a location "
                                                                      "in this multiverse...")
            return
        self._handleCommandWithLocation(server, source, command, location)

    def _handleCommandWithLocation(self, server, source, command, location):
        weather = ""
        if command == "weather":
            weather = self._getWeather(location["latitude"], location["longitude"])
        elif command == "forecast":
            weather = self._getForecast(location["latitude"], location["longitude"])
        self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Location: {} | {}".format(location["locality"],
                                                                                             weather))

    def _getWeather(self, lat, lon):
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.apiKey
        }
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", self.weatherBaseURL, params)
        if not result:
            return "No weather for this location could be found at this moment. Try again later."
        if not result.json()["cod"] == 200:
            return "No weather for this location could be found."
        return self._parseWeather(result.json())

    def _getForecast(self, lat, lon):
        params = {
            "lat": lat,
            "lon": lon,
            "cnt": 4,
            "appid": self.apiKey
        }
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", self.forecastBastURL, params)
        if not result:
            return "No forecast for this location could be found at this moment. Try again later."
        if not result.json()["cod"] == "200":
            return "No forecast for this location could be found."
        return self._parseForecast(result.json())

    def _parseWeather(self, json):
        tempK = float(json["main"]["temp"])
        tempC = round((tempK - 273.15), 1)
        tempF = round((tempK - 273.15) * 9 / 5 + 32, 1)
        description = json["weather"][0]["description"].title()
        if "humidity" in json["main"]:
            humidity = "{}%".format(json["main"]["humidity"])
        else:
            humidity = "Unknown"
        windspeed = json["wind"]["speed"]
        windspeedMiles = round(windspeed, 1)
        windspeedKmph = round(windspeed * 1.60934, 1)
        if "deg" in json["wind"]:
            winddir = self._convertWindDegToCardinal(float(json["wind"]["deg"]))
        else:
            winddir = "Unknown"
        latestUpdate = (timestamp(now()) - int(json["dt"])) / 60
        latestUpdateStr = "{} minute(s) ago".format(latestUpdate) if latestUpdate > 0 else "just now"
        return "Temp: {}°C / {}°F | Weather: {} | Humidity: {} | Wind Speed: {} kmph / {} mph | Wind Direction: {} | " \
               "Latest Update: {}.".format(tempC, tempF, description, humidity, windspeedKmph, windspeedMiles,
                                           winddir, latestUpdateStr)

    def _parseForecast(self, json):
        daysList = json["list"]
        formattedDays = []
        for x in range(0, len(daysList)):
            day = daysList[x]
            date = datetime.fromtimestamp(int(day["dt"])).strftime("%A")
            minK = float(day["temp"]["min"])
            maxK = float(day["temp"]["max"])
            minC = round((minK - 273.15), 1)
            minF = round((minK - 273.15) * 9 / 5 + 32, 1)
            maxC = round((maxK - 273.15), 1)
            maxF = round((maxK - 273.15) * 9 / 5 + 32, 1)
            description = day["weather"][0]["description"].title()
            formattedDays.append("{}: {} - {}°C, {} - {}°F, {}".format(date, minC, maxC, minF, maxF, description))
        return " | ".join(formattedDays)

    def _convertWindDegToCardinal(self, degrees):
        directions = [ "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW",
                       "NNW" ]
        i = int((degrees + 11.25) / 22.5)
        return directions[i % 16]

weatherCommand = WeatherCommand()
