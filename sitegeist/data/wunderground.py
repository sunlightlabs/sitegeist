from django.conf import settings
import requests

STATION_ENDPOINT = "http://api.wunderground.com/api/%s/almanac/q/%s,%s.json"


def almanac(lat, lon):

    url = STATION_ENDPOINT % (settings.WUNDERGROUND_KEY, lat, lon)

    resp = requests.get(url)
    return resp.json['almanac']
