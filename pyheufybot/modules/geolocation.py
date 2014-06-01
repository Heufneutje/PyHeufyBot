import json
from pyheufybot.modulehandler import Module, ModuleAccessLevel, ModulePriority, ModuleType
from pyheufybot.utils.webutils import fetchURL

class ModuleSpawner(Module):
    baseAPIAddress = "http://maps.googleapis.com/maps/api/geocode/json?"

    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "GeoLocation"
        self.moduleType = ModuleType.PASSIVE
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ANYONE
        self.messageTypes = []
        self.helpText = "Provides a geocoding interface for other modules to use."

    def execute(self, message):
        return True

    def getGeoLocationFromLatLon(self, latitude, longitude):
        url = "{}latlng={},{}&sensor=false&language=english".format(self.baseAPIAddress, latitude, longitude)
        return self._getLocationFromJSON(self._getJSON(url))

    def getGeoLocationFromPlace(self, place):
        place = place.replace(" ", "+")
        url = "{}address={}&sensor=false".format(self.baseAPIAddress, place)
        return self._getLocationFromJSON(self._getJSON(url))

    def _getLocationFromJSON(self, jsonString):
        if jsonString["status"] == "OK":
            firstHit = jsonString["results"][0]
            locality = self._siftForCreepy(firstHit["address_components"])
            latitude = float(firstHit["geometry"]["location"]["lat"])
            longitude = float(firstHit["geometry"]["location"]["lng"])
            return [locality, latitude, longitude]
        else:
            return None

    def _getJSON(self, url):
        return json.loads(fetchURL(url).body)

    def _siftForCreepy(self, addressComponents):
        locationInfo = []
        safeList = ["locality", "administrative_area_level_1", "country", "natural_feature", "colloquial_area"]
        for location in addressComponents:
            if len(set(safeList).intersection(location["types"])) > 0:
                locationInfo.append(location["long_name"])
        return ", ".join(locationInfo)
