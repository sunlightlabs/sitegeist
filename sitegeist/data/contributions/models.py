from django.db import models


class Contribution(models.Model):
    zipcode = models.CharField(max_length=5)
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    republicans = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    democrats = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)\

    class Meta:
        ordering = ('zipcode',)

    def __unicode__(self):
        return self.zipcode
