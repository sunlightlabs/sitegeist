from django.conf import settings
import requests

API_KEY = settings.DARKSKY_KEY
ENDPOINT = "https://api.darkskyapp.com/v1/forecast/%s/%s,%s"


def forecast(lat, lon):

    url = ENDPOINT % (API_KEY, lat, lon)

    resp = requests.get(url)
    return resp.json
