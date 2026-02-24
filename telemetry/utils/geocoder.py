from abc import abstractmethod, ABC

import requests
from requests import RequestException

from vehicles.settings import GEOAPIFY_API_KEY, GEOCODER, LOCATIONIQ_API_KEY, DADATA_API_KEY, YANDEX_API_KEY, \
    ORS_API_KEY


def get_coordinates(address):
    try:
        url = f"https://api.geoapify.com/v1/geocode/search?text={address}&limit=1&format=json&apiKey={GEOAPIFY_API_KEY}"
        response = requests.get(url)
        data = response.json()

        print(f"Address: {address}")
        print(f"Response: {data}")

        if "results" in data and data["results"]:
            first = data["results"][0]
            lat = first.get("lat")
            lon = first.get("lon")
            if lat is not None and lon is not None:
                return float(lat), float(lon)
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

class Geocoder(ABC):

    @abstractmethod
    def get_address(self, lat: float, lon: float) -> str:
        pass

class Geoapify(Geocoder):
    name = "geoapify"

    def get_address(self, lat: float, lon: float) -> str:
        try:
            url = f"https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&format=json&lang=ru&apiKey={GEOAPIFY_API_KEY}"
            response = requests.get(url)
            data = response.json()
            if (response.status_code == 200 and data.get("results") and len(data["results"]) > 0):
                address = data["results"][0]["formatted"]
                return address
            return "Адрес неизвестен"
        except Exception:
            return "Адрес неизвестен"


class Nominatim(Geocoder):
    name = "nominatim"

    def get_address(self, lat: float, lon: float) -> str:
        url = "https://nominatim.openstreetmap.org/reverse"
        headers = {"User-Agent": "Vehicles/1.0"}
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "accept-language": "ru"
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            if (response.status_code == 200 and data.get("display_name")):
                return data["display_name"]
            return "Адрес неизвестен"
        except Exception:
            return "Адрес неизвестен"

class LocationIQ(Geocoder):
    name = "locationiq"

    def get_address(self, lat: float, lon: float) -> str:
        url = f"https://us1.locationiq.com/v1/reverse?lat={lat}&lon={lon}&format=json&accept-language=ru&key={LOCATIONIQ_API_KEY}"
        try:
            response = requests.get(url)
            data = response.json()
            if (response.status_code == 200 and data.get("display_name")):
                return data["display_name"]
            return "Адрес неизвестен"
        except Exception:
            return "Адрес неизвестен"

class DaData(Geocoder):
    name = "dadata"

    def get_address(self, lat: float, lon: float) -> str:
        url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/geolocate/address"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Token {DADATA_API_KEY}",
        }
        payload = {
            "lat": lat,
            "lon": lon,
            "count": 1,
            "language": "ru"
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()
            if (response.status_code == 200 and data.get("suggestions") and len(data["suggestions"]) > 0):
                address = data["suggestions"][0]["value"]
                return address
            return "Адрес неизвестен"
        except Exception:
            return "Адрес неизвестен"

class Yandex(Geocoder):
    name = "yandex"

    def get_address(self, lat: float, lon: float) -> str:
        url = f"https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": YANDEX_API_KEY,
            "geocode": f"{lon},{lat}",
            "format": "json",
            "lang": "ru_RU",
            "kind": "house",
            "results": 1,
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()
            if data["response"]["GeoObjectCollection"]["metaDataProperty"]["GeocoderResponseMetaData"]["found"] == "0":
                return "Адрес неизвестен"

            address = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]
            return address
        except Exception:
            return "Адрес неизвестен"

class OpenRouteService(Geocoder):
    name = "openrouteservice"

    def get_address(self, lat: float, lon: float) -> str:
        url = "https://api.openrouteservice.org/geocode/reverse"
        headers = {
            "Authorization": f"Bearer {ORS_API_KEY}",
            "Accept": "application/json",
        }
        params = {
            "point.lon": lon,
            "point.lat": lat,
            "size": 1,
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            if (response.status_code == 200 and data.get("features")):
                props = data["features"][0].get("properties", {})
                address = []
                for key in ["housenumber", "street", "region", "country", "postalcode"]:
                    if props.get(key):
                        address.append(str(props[key]))
                if address:
                    return ", ".join(address)
            return "Адрес неизвестен"

        except Exception:
            return "Адрес неизвестен"

def get_address(lat: float, lon: float) -> str:
    geocoder = Geoapify()
    if GEOCODER == "nominatim":
        geocoder = Nominatim()
    elif GEOCODER == "locationiq":
        geocoder = LocationIQ()
    elif GEOCODER == "dadata":
        geocoder = DaData()
    elif GEOCODER == "yandex":
        geocoder = Yandex()
    elif GEOCODER == "openrouteservice":
        geocoder = OpenRouteService()
    return geocoder.get_address(lat, lon)