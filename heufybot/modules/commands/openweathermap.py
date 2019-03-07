# -*- coding: utf-8 -*-
from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements
from datetime import datetime
import time


class OpenWeatherMapCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "OpenWeatherMap"
    weatherBaseURL = "https://api.openweathermap.org/data/2.5"

    def triggers(self):
        return ["forecast", "weather"]

    def load(self):
        self.help = "Commands: weather/forecast <lat> <lon>, weather/forecast <place>, weather/forecast <nickname> " \
                    "| Get the current weather conditions or forecast for the given latlon, place or user."
        self.commandHelp = {
            "forecast": "forecast <lat> <lon>, forecast <place>, forecast <nickname> | Get the forecast for the given " \
                        "latlon, place or user.",
            "weather": "weather <lat> <lon>, weather <place>, weather <nickname> | Get the current weather condidions " \
                       "for the given latlon, place or user."
        }
        self.apiKey = None
        if "openweathermap" in self.bot.storage["api-keys"]:
            self.apiKey = self.bot.storage["api-keys"]["openweathermap"]

    def execute(self, server, source, command, params, data):
        if not self.apiKey:
            self.replyPRIVMSG(server, source, "No API key found.")
            return

        # Use the user"s nickname as a parameter if none were given
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

        # Try to determine the user"s location from a nickname
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
        place = " ".join(params)
        if place.startswith("pws:") and command in ["weather", "forecast"]:
            place = place[4:]
            location = {"success": True, "pws": place, "locality": "Weather Station {}".format(place)}
        else:
            location = self.bot.moduleHandler.runActionUntilValue("geolocation-place", place)
        if not location:
            self.replyPRIVMSG(server, source, "I can't determine locations at the moment. Try again later.")
            return
        if not location["success"]:
            self.replyPRIVMSG(server, source, "I don't think that's even a location in this multiverse...")
            return
        self._handleCommandWithLocation(server, source, command, location)

    def _handleCommandWithLocation(self, server, source, command, location):
        request = command
        params = {
            "lat": location["latitude"],
            "lon": location["longitude"],
            "units": "metric",
            "appid": self.apiKey
        }

        if request == "forecast":
            request = "forecast/daily"
            params["cnt"] = 4

        url = "{}/{}".format(self.weatherBaseURL, request)
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", url, params)
        output = None
        if not result:
            output = "No weather for this location could be found at this moment. Try again later."
        else:
            j = result.json()
            if "cod" not in j:
                output = "The OpenWeatherMap API returned an unknown reply."
            elif int(j["cod"]) != 200 and "message" in j:
                output = "The OpenWeatherMap API returned an error:{}".format(j["message"])
            elif int(j["cod"]) == 200:
                if command == "weather":
                    output = _parseWeather(j)
                elif command == "forecast":
                    output = _parseForecast(j)
        self.replyPRIVMSG(server, source, "Location: {} | {}".format(location["locality"], output))


def _parseWeather(json):
    description = json["weather"][0]["main"]
    main = json["main"]
    tempC = round(main["temp"], 1)
    tempF = round(_celsiusToFahrenheit(main["temp"]), 1)
    humidity = main["humidity"]

    wind = json["wind"]
    winddir = _getWindDirection(wind["deg"])
    windspeedMs = round(wind["speed"], 1)
    windspeedMph = round(_msToMph(wind["speed"]), 1)
    windspeedBft = _msToBft(wind["speed"])

    if "gust" in wind:
        gustsMs = round(wind["gust"], 1)
        gustsMph = round(_msToMph(wind["gust"]), 1)
        gustsBft = _msToBft(wind["gust"])
        gustStr = "Gust Speed: {} m/s / {} mph / {} BFT | ".format(gustsMs, gustsMph, gustsBft)
    else:
        gustStr = ""

    dataAge = int(round((time.time() - json["dt"]) / 60))
    if dataAge <= 0:
        dataAgeStr = "just now"
    else:
        dataAgeStr = "{} minute{} ago".format(dataAge, "s" if dataAge > 1 else "")

    return "Temp: {}°C / {}°F | Weather: {} | Humidity: {}% | Wind Speed: {} m/s / {} mph / {} BFT | {}Wind " \
           "Direction: {} | Latest Update: {}.".format(tempC, tempF, description, humidity, windspeedMs,
                                                       windspeedMph, windspeedBft, gustStr, winddir, dataAgeStr)


def _parseForecast(json):
    daysList = json["list"]
    formattedDays = []
    for x in range(0, len(daysList)):
        day = daysList[x]
        date = datetime.utcfromtimestamp(day['dt']).strftime("%A")
        minC = round(day["temp"]["min"], 1)
        minF = round(_celsiusToFahrenheit(day["temp"]["min"]), 1)
        maxC = round(day["temp"]["max"], 1)
        maxF = round(_celsiusToFahrenheit(day["temp"]["max"]), 1)
        description = day["weather"][0]["main"]
        formattedDays.append("{}: {} - {}°C, {} - {}°F, {}".format(date, minC, maxC, minF, maxF, description))
    return " | ".join(formattedDays)


def _getWindDirection(angle):
    windDirectionTranslation = {
        11.25: "N",
        33.75: "NNE",
        56.25: "NE",
        78.75: "ENE",
        101.25: "E",
        123.75: "ESE",
        146.25: "SE",
        168.75: "SSE",
        191.25: "S",
        213.75: "SSW",
        236.25: "SW",
        258.75: "WSW",
        281.25: "W",
        303.75: "WNW",
        326.25: "NW",
        348.75: "NNW",
        360.0: "N"
    }
    windDirection = "N"
    for maxDegrees in sorted(windDirectionTranslation.keys()):
        if angle < maxDegrees:
            break
        else:
            windDirection = windDirectionTranslation[maxDegrees]
    return windDirection


def _celsiusToFahrenheit(celsius):
    return (celsius * 9 / 5) + 32


def _msToMph(windMs):
    return windMs * 2.237


def _msToBft(windMs):
    windSpeedTranslation = {
        0.2: 1,
        1.5: 2,
        3.3: 3,
        5.4: 4,
        7.9: 5,
        10.7: 6,
        13.8: 7,
        17.1: 8,
        20.7: 9,
        24.4: 10,
        28.4: 11,
        32.6: 12,
        32.7: 13
    }
    windSpeed = 0
    for maxSpeed in sorted(windSpeedTranslation.keys()):
        if windMs < maxSpeed:
            break
        else:
            windSpeed = windSpeedTranslation[maxSpeed]
    return windSpeed


openWeatherMapCommand = OpenWeatherMapCommand()
