from django.contrib.gis.db import models

class Site(models.Model):
    objects = models.GeoManager()
    url = models.URLField()
    point = models.PointField()

