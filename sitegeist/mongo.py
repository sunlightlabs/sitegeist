from django.conf import settings

import pymongo


def connect(db="sitegeist"):
    conn = pymongo.Connection(settings.MONGO_URI)
    return conn[db]

db = connect()


# helper methods

def create_indexes():

    expsecs = settings.SITEGEIST['COORDCACHE_EXPIRATION'] * 60

    db.coordcache.drop()

    db.coordcache.ensure_index([("geo", pymongo.GEO2D)])
    db.coordcache.ensure_index([("timestamp", pymongo.DESCENDING)], expiresAfterSeconds=expsecs)
