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
    weatherBaseURL = "http://api.wunderground.com/api"

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
        if "wunderground" in self.bot.storage["api-keys"]:
            self.apiKey = self.bot.storage["api-keys"]["wunderground"]

    def execute(self, server, source, command, params, data):
        if not self.apiKey:
            self.replyPRIVMSG(server, source, "No API key found.")
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
                self.replyPRIVMSG(server, source, "I can't determine locations at the moment. Try again later.")
                return
            if not location["success"]:
                self.replyPRIVMSG(server, source, "I don't think that's even a location in this multiverse...")
                return
            self._handleCommandWithLocation(server, source, command, location)
            return
        except (IndexError, ValueError):
            pass  # The user did not give a latlon, so continue using other methods

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
                    self.replyPRIVMSG(server, source, "I can't determine locations at the moment. Try again later.")
                    return
                if not location["success"]:
                    self.replyPRIVMSG(server, source, "I don't think that's even a location in this multiverse...")
                    return
                self._handleCommandWithLocation(server, source, command, location)
                return

        # Try to determine the location by the name of the place
        location = self.bot.moduleHandler.runActionUntilValue("geolocation-place", " ".join(params))
        if not location:
            self.replyPRIVMSG(server, source, "I can't determine locations at the moment. Try again later.")
            return
        if not location["success"]:
            self.replyPRIVMSG(server, source, "I don't think that's even a location in this multiverse...")
            return
        self._handleCommandWithLocation(server, source, command, location)

    def _handleCommandWithLocation(self, server, source, command, location):
        weather = ""
        if command == "weather":
            weather = self._getWeather(location["latitude"], location["longitude"])
        elif command == "forecast":
            weather = self._getForecast(location["latitude"], location["longitude"])
        self.replyPRIVMSG(server, source, "Location: {} | {}".format(location["locality"], weather))

    def _getWeather(self, lat, lon):
        url = "{}/{}/conditions/q/{},{}.json".format(self.weatherBaseURL, self.apiKey, lat, lon)
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", url)
        if not result:
            return "No weather for this location could be found at this moment. Try again later."
        j = result.json()
        if "error" in j["response"]:
            return "The weather API returned an error of type {}.".format(j["response"]["error"]["type"])
        return self._parseWeather(j)

    def _getForecast(self, lat, lon):
        url = "{}/{}/forecast/q/{},{}.json".format(self.weatherBaseURL, self.apiKey, lat, lon)
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", url)
        if not result:
            return "No forecast for this location could be found at this moment. Try again later."
        j = result.json()
        if "error" in j["response"]:
            return "The weather API returned an error of type {}.".format(j["response"]["error"]["type"])
        return self._parseForecast(j)

    def _parseWeather(self, json):
        cond = json["current_observation"]
        tempC = cond["temp_c"]
        tempF = cond["temp_f"]
        feelslikeC = cond["feelslike_c"]
        feelslikeF = cond["feelslike_f"]
        description = cond["weather"]
        humidity = cond["relative_humidity"]
        winddir = cond["wind_dir"]
        windspeedMiles = cond["wind_mph"]
        windspeedMs = round(cond["wind_kph"] / 3.6, 1)
        tempDiff = float(tempC) - float(feelslikeC)
        feelslikeStr = ""
        if tempDiff > 3.0 or tempC < -3.0:
            feelslikeStr = "(feels like {}°C / {}°F) ".format(feelslikeC, feelslikeF)

        if len(cond["estimated"]) > 0:
            estimate = cond["estimated"]["description"]
            return "Temp: {}°C / {}°F {}| Weather: {} | Humidity: {} | Wind Speed: {} m/s / {} mph | " \
                   "Wind Direction: {} | {}".format(tempC, tempF, feelslikeStr, description, humidity, windspeedMs,
                                                     windspeedMiles, winddir, estimate)

        latestUpdate = (timestamp(now()) - int(cond["observation_epoch"])) / 60
        latestUpdateStr = "{} minute(s) ago".format(latestUpdate) if latestUpdate > 0 else "just now"
        return "Temp: {}°C / {}°F {}| Weather: {} | Humidity: {} | Wind Speed: {} m/s / {} mph | " \
               "Wind Direction: {} | Latest Update: {}.".format(tempC, tempF, feelslikeStr, description, humidity,
                                                                windspeedMs, windspeedMiles, winddir, latestUpdateStr)

    def _parseForecast(self, json):
        daysList = json["forecast"]["simpleforecast"]["forecastday"]
        formattedDays = []
        for x in range(0, len(daysList)):
            day = daysList[x]
            date = day["date"]["weekday"]
            minC = day["low"]["celsius"]
            minF = day["low"]["fahrenheit"]
            maxC = day["high"]["celsius"]
            maxF = day["high"]["fahrenheit"]
            description = day["conditions"]
            formattedDays.append("{}: {} - {}°C, {} - {}°F, {}".format(date, minC, maxC, minF, maxF, description))
        return " | ".join(formattedDays)


weatherCommand = WeatherCommand()
