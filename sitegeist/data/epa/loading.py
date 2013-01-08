import csv
import os

from django.conf import settings
from django.contrib.gis.geos import fromstr

from sitegeist.data.epa.models import Site


def load():

    Site.objects.all().delete()

    path = os.path.join(settings.SITEGEIST['DATA_CACHE'], 'epa', 'contaminated.csv')
    with open(path) as infile:

        for (lat, lon, url) in csv.reader(infile):

            if lat and lon:

                pnt = fromstr('POINT(%s %s)' % (lon, lat), srid=4326)
                Site.objects.create(url=url, point=pnt)


if __name__ == "__main__":
    load()
