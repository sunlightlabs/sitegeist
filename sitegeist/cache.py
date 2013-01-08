import datetime
import logging

from django.conf import settings

from sitegeist.mongo import db

logger = logging.getLogger(__name__)


class CoordinateCache(object):

    def __init__(self, namespace, snap_radius=None):
        self.namespace = namespace
        self.snap_radius = snap_radius or settings.SITEGEIST['GEO_SNAP_RADIUS']

    def get(self, latlon):

        if not settings.SITEGEIST.get('COORDCACHE', False):
            return

        latlon = [float(p) for p in latlon]

        spec = {
            "namespace": self.namespace,
            "geo": {
                "$maxDistance": self.snap_radius,
                "$near": latlon
            }
        }

        doc = db.coordcache.find_one(spec)

        if doc:

            now = datetime.datetime.utcnow()

            expsecs = settings.SITEGEIST['COORDCACHE_EXPIRATION'] * 60
            exptime = doc['timestamp'] + datetime.timedelta(seconds=expsecs)

            logger.debug("Comparing cache expiration %s to now %s" % (exptime, now))

            if exptime > now:
                logger.debug("Cache is valid")
                return doc['data']
            else:
                logger.debug("Cache is invalid, deleting document")
                db.coordcache.remove(doc["_id"])

    def set(self, latlon, data):

        doc = {
            'geo': latlon,
            'namespace': self.namespace,
            'data': data,
            'timestamp': datetime.datetime.utcnow(),
        }

        db.coordcache.insert(doc)
