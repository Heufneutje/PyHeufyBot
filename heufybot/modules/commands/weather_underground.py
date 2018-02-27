# -*- coding: utf-8 -*-
from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils.timeutils import now, timestamp
from zope.interface import implements


class WeatherUndergroundCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "WeatherUnderground"
    weatherBaseURL = "http://api.wunderground.com/api"

    def triggers(self):
        return ["astronomy", "forecast", "walert", "weather"]

    def load(self):
        self.help = "Commands: weather/forecast/astronomy/walert <lat> <lon>, weather/forecast/astronomy/walert " \
                    "<place>, weather/forecast/astronomy/walert <nickname>, | Get the current weather conditions, " \
                    "forecast, astronomy or weather alerts for the given latlon, place or user."
        self.commandHelp = {
            "astronomy": "astronomy <lat> <lon>, astronomy <place>, astronomy <nickname> | Get moon phase, sunrise and " \
                         "sunset times for the given latlon, place or user.",
            "forecast": "forecast <lat> <lon>, forecast <place>, forecast <nickname> | Get the forecast for the given " \
                        "latlon, place or user.",
            "walert": "walert <lat> <lon>, walert <place>, walert <nickname> | Get the weather alerts for the given " \
                      "latlon, place or user.",
            "weather": "weather <lat> <lon>, weather <place>, weather <nickname> | Get the current weather condidions " \
                       "for the given latlon, place or user."
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
            self._handleCommandWithLocation(server, source, _getFeature(command), location)
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
                self._handleCommandWithLocation(server, source, _getFeature(command), location)
                return

        # Try to determine the location by the name of the place
        location = self.bot.moduleHandler.runActionUntilValue("geolocation-place", " ".join(params))
        if not location:
            self.replyPRIVMSG(server, source, "I can't determine locations at the moment. Try again later.")
            return
        if not location["success"]:
            self.replyPRIVMSG(server, source, "I don't think that's even a location in this multiverse...")
            return
        self._handleCommandWithLocation(server, source, _getFeature(command), location)

    def _handleCommandWithLocation(self, server, source, command, location):
        apiFunction = "conditions" if command == "weather" else command
        url = "{}/{}/{}/q/{},{}.json".format(self.weatherBaseURL, self.apiKey, apiFunction, location["latitude"],
                                             location["longitude"])
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", url)
        output = None
        if not result:
            output = "No weather for this location could be found at this moment. Try again later."
        else:
            j = result.json()
            if "error" in j["response"]:
                output = "The Weather Underground API returned an error of type {}.".format(
                         j["response"]["error"]["type"])
            else:
                if command == "weather":
                    output = _parseWeather(j)
                elif command == "forecast":
                    output = _parseForecast(j)
                elif command == "astronomy":
                    output = _parseAstronomy(j)
                elif command == "alerts":
                    output = self._parseAlert(j)
        self.replyPRIVMSG(server, source, "Location: {} | {}".format(location["locality"], output))

    def _parseAlert(self, json):
        alerts = json["alerts"]
        if len(alerts) == 0:
            return "No weather alerts were found."
        if "wtype_meteoalarm_name" in alerts[0]:
            alertType = alerts[0]["wtype_meteoalarm_name"]
        elif "description" in alerts[0]:
            alertType = alerts[0]["description"]
        elif "type" in alerts[0]:
            alertType = alerts[0]["type"]
        else:
            alertType = "Unknown"
        if "level_meteoalarm_name" in alerts[0]:
            level = alerts[0]["level_meteoalarm_name"]
        else:
            level = "None"
        description = alerts[0]["message"].encode("utf-8", "ignore").replace("\n", " ")
        if description.endswith(">)"):
            description = description[:-2]  # Strip WUnderground weirdness.
        if len(description) > 275:
            result = self.bot.moduleHandler.runActionUntilValue("post-paste", "Weather alert", description, 10)
            if result:
                description = "{}... {}".format(description[:250], result)
        return "Type: {} | Level: {} | {}".format(alertType, level, description)


def _parseWeather(json):
    if "current_observation" not in json:
        return "No weather for this location could be found at this moment. Try again later."

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
    stationID = cond["station_id"]
    feelslikeStr = ""
    if abs(float(tempC) - float(feelslikeC)) > 3.0:
        feelslikeStr = "(feels like {}°C / {}°F) ".format(feelslikeC, feelslikeF)

    if len(cond["estimated"]) > 0:
        latestUpdateStr = cond["estimated"]["description"]
    else:
        latestUpdate = (timestamp(now()) - int(cond["observation_epoch"])) / 60
        latestUpdateStr = "Latest Update: {}".format("{} minute(s) ago".format(latestUpdate) if latestUpdate > 0 \
                                                         else "just now")

    return "Temp: {}°C / {}°F {}| Weather: {} | Humidity: {} | Wind Speed: {} m/s / {} mph | " \
            "Wind Direction: {} | Station ID: {} | {}.".format(tempC, tempF, feelslikeStr, description, humidity,
                                                               windspeedMs,  windspeedMiles, winddir, stationID,
                                                               latestUpdateStr)


def _parseForecast(json):
    if "forecast" not in json:
        return "No forecast for this location could be found at this moment. Try again later."

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

def _parseAstronomy(json):
    astr = json["moon_phase"]
    phase = astr["phaseofMoon"]
    sunrise = _getTimeString(astr["sunrise"]["hour"], astr["sunrise"]["minute"])
    sunset = _getTimeString(astr["sunset"]["hour"], astr["sunset"]["minute"])
    moonrise = _getTimeString(astr["moonrise"]["hour"], astr["moonrise"]["minute"])
    moonset = _getTimeString(astr["moonset"]["hour"], astr["moonset"]["minute"])

    return "Tonight's Moon Phase: {} | Sunrise: {}, Sunset: {} | Moonrise: {}, Moonset: {}".format(phase, sunrise,
                                                                                                   sunset, moonrise,
                                                                                                   moonset)

def _getTimeString(hours, minutes):
    try:
        hours = int(hours)
        hour24 = "{}:{}".format(hours, minutes)
        hour12 = "{}:{} {}".format(hours if hours < 13 else hours - 12, minutes, "AM" if hours < 13 else "PM")
        return "{} ({})".format(hour24, hour12)
    except ValueError:
        return "Unknown"

def _getFeature(command):
    if command == "walert":
        return "alerts"
    return command

weatherUndergroundCommand = WeatherUndergroundCommand()
