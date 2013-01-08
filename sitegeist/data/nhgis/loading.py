import csv
import os

from django.conf import settings

from sitegeist.data.nhgis.models import Tract


def load():

    Tract.objects.all().delete()

    path = os.path.join(settings.SITEGEIST['DATA_CACHE'], 'nhgis', 'nhgis0001_ts_tract.csv')
    with open(path) as infile:

        count = 0

        reader = csv.DictReader(infile)

        for rec in reader:

            if count == 0:
                count += 1
                continue

            Tract.objects.create(
                state=rec['STATEA'],
                county=rec['COUNTYA'],
                tract=rec['TRACT'],
                year=rec['YEAR'],
                units=int(rec['A41AA'])
            )

            count += 1


if __name__ == "__main__":
    load()
