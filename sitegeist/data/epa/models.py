from django.contrib.gis.db import models

class Site(models.Model):
    objects = models.GeoManager()
    url = models.URLField(verify_exists=False)
    point = models.PointField()

