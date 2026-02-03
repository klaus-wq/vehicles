import requests
from vehicles.settings import GEOAPIFY_API_KEY


def get_address(lat, lng):
    try:
        url = f"https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lng}&format=json&lang=ru&apiKey={GEOAPIFY_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if (response.status_code == 200 and data.get("results") and len(data["results"]) > 0):
            address = data["results"][0]["formatted"]
            return address
        return "Адрес неизвестен"
    except Exception:
        return "Адрес неизвестен"