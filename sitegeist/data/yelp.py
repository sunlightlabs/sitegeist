from django.conf import settings
from oauth_hook import OAuthHook
import requests

ENDPOINT = "http://api.yelp.com/v2/search"

BASE_CATEGORIES = "active,arts,food,nightlife,restaurants"

METERS_PER_MILE = 1609

oauth_hook = OAuthHook(
    settings.YELP['TOKEN'],
    settings.YELP['TOKEN_SECRET'],
    settings.YELP['CONSUMER_KEY'],
    settings.YELP['CONSUMER_SECRET'])

http = requests.session(hooks={'pre_request': oauth_hook})

default_filters = {
    'limit': 20,
    'sort': 2,  # highest rated
    'radius_filter': METERS_PER_MILE * 3,  # in meters, roughly 3 miles
}


def nearby(lat, lon, categories=None, radius=None, limit=None):

    filters = default_filters.copy()
    filters['ll'] = "%s,%s" % (lat, lon)

    if categories:
        filters['category_filter'] = categories

    if radius:
        filters['radius_filter'] = radius

    if limit:
        filters['limit'] = limit

    resp = http.get(ENDPOINT, params=filters)

    data = resp.json
    return data['businesses'] if data and 'businesses' in data else []


def test():

    lat = "39.138765"
    lon = "-77.197970"

    # recommended
    nearby(lat, lon, categories=BASE_CATEGORIES)

    # local flavor
    ten_miles = METERS_PER_MILE * 10
    nearby(lat, lon, categories='localflavor', radius=ten_miles)
