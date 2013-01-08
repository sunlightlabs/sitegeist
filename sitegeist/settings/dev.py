import dj_database_url
from common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# data sources

DATABASES = {'default': dj_database_url.parse('postgis://localhost:5432/sitegeist')}

MONGO_URI = "mongodb://localhost/"

# Sitegeist config

SITEGEIST = {
    'DATA_CACHE': '',  # set to same value that is in config/loading.ini
    'GEO_SNAP_RADIUS': 1,  # in meters
    'COORDCACHE_EXPIRATION': 1,  # in minutes
    'COORDCACHE': True,
}

# API keys

SUNLIGHT_KEY = ''
CENSUS_KEY = ''

YELP = {
    'CONSUMER_KEY': '',
    'CONSUMER_SECRET': '',
    'TOKEN': '',
    'TOKEN_SECRET': '',
}

FOURSQUARE = {
    'CLIENT_ID': '',
    'CLIENT_SECRET': '',
}

DARKSKY_KEY = ""
WUNDERGROUND_KEY = ""

SENTRY_DSN = ""
