from django.db import models


class Tract(models.Model):

    state = models.CharField(max_length=2)
    county = models.CharField(max_length=3)
    tract = models.CharField(max_length=12)

    year = models.CharField(max_length=4)
    units = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ('state', 'county', 'tract')

    def __unicode__(self):
        return u"%s:%s:%s" % (self.state, self.county, self.tract)
