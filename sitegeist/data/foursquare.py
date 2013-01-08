from django.conf import settings
import requests

API_VERSION = "20121120"

MOVIE_THEATERS = "4bf58dd8d48988d17f941735"


def explore(lat, lon):

    endpoint = "https://api.foursquare.com/v2/venues/explore"

    params = {
        'll': "%s,%s" % (lat, lon),
        'radius': 1500,  # meters
        'client_id': settings.FOURSQUARE['CLIENT_ID'],
        'client_secret': settings.FOURSQUARE['CLIENT_SECRET'],
        'limit': 1,
        'section': 'topPicks',
        'v': API_VERSION,
    }

    resp = requests.get(endpoint, params=params)

    try:

        location = resp.json["response"]["groups"][0]["items"][0]

        data = {
            "id": location["venue"]["id"],
            "name": location["venue"]["name"],
            "rating": location["venue"].get("rating"),
            "url": location["venue"].get("url"),
            "stats": location["venue"]["stats"],
            "reason": ", ".join(r["summary"] for r in location["reasons"]["items"])
        }

    except Exception, e:
        print e
        data = {}

    return data


def search(lat, lon, category=None):

    endpoint = "https://api.foursquare.com/v2/venues/search"

    params = {
        'll': "%s,%s" % (lat, lon),
        'radius': 1500,  # meters
        'client_id': settings.FOURSQUARE['CLIENT_ID'],
        'client_secret': settings.FOURSQUARE['CLIENT_SECRET'],
        'limit': 5,
        'intent': 'browse',
        'v': API_VERSION,
    }

    if category:
        params['categoryId'] = category

    resp = requests.get(endpoint, params=params)

    try:
        return resp.json["response"]["venues"]
    except:
        pass

    # try:

    #     for location in resp.json["response"]

    #     location = resp.json["response"]["groups"][0]["items"][0]

    #     data = {
    #         "id": location["venue"]["id"],
    #         "name": location["venue"]["name"],
    #         "rating": location["venue"].get("rating"),
    #         "url": location["venue"].get("url"),
    #         "stats": location["venue"]["stats"],
    #         "reason": ", ".join(r["summary"] for r in location["reasons"]["items"])
    #     }

    # except Exception, e:
    #     print e
    #     data = []

    # return data
