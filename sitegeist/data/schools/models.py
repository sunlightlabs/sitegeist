from django.contrib.gis.db import models

LOCALES = (
    ('11', 'City, Large'),
    ('12', 'City, Mid-size'),
    ('13', 'City, Small'),
    ('21', 'Suburb, Large'),
    ('22', 'Suburb, Mid-size'),
    ('23', 'Suburb, Small'),
    ('31', 'Town, Fringe'),
    ('32', 'Town, Distant'),
    ('33', 'Town, Remote'),
    ('41', 'Rural, Fringe'),
    ('42', 'Rural, Distant'),
)

TYPES = (
    ('1', 'Elementary and secondary'),
    ('2', 'Special education'),
    ('3', 'Vocational and technical'),
    ('4', 'Other'),
    ('5', 'Reportable program'),
)

LEVEL_CODES = (
    ('1', 'Primary'),
    ('2', 'Middle'),
    ('3', 'High'),
    ('4', 'Other'),
)

LEVELS = (
    ('PK', 'PreKindergarten'),
    ('KG', 'Kindergarten'),
    ('01', '1st grade'),
    ('02', '2nd grade'),
    ('03', '3rd grade'),
    ('04', '4th grade'),
    ('05', '5th grade'),
    ('06', '6th grade'),
    ('07', '7th grade'),
    ('08', '8th grade'),
    ('09', '9th grade'),
    ('10', '10th grade'),
    ('11', '11th grade'),
    ('12', '12th grade'),
    ('UG', 'Ungraded'),
    ('00', 'No students'),
)

STATUSES = (
    ('1', 'Operational'),
    ('2', 'Closed'),
    ('3', 'New'),
    ('4', 'Not previously reported'),
    ('5', 'Changed agency'),
    ('6', 'Temporarily closed'),
    ('7', 'Future school'),
    ('8', 'Reopened'),
)

class School(models.Model):

    objects = models.GeoManager()

    nces_id = models.CharField(max_length=12)
    name = models.CharField(max_length=128)
    street = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zipcode = models.CharField(max_length=5, blank=True)
    enrollment = models.IntegerField(blank=True, null=True)
    locale_code = models.CharField(max_length=2, choices=LOCALES, blank=True)
    type_code = models.CharField(max_length=1, choices=TYPES, blank=True)
    level_code = models.CharField(max_length=1, choices=LEVEL_CODES, blank=True)
    level_low = models.CharField(max_length=2, choices=LEVELS, blank=True)
    level_high = models.CharField(max_length=2, choices=LEVELS, blank=True)
    status = models.CharField(max_length=1, choices=STATUSES, blank=True)

    lon = models.FloatField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name
