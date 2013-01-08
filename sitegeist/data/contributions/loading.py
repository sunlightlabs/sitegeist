import csv
import os

from django.conf import settings

from sitegeist.data.contributions.models import Contribution


def reset():
    Contribution.objects.all().delete()


def load_contributions():

    cache_dir = settings.SITEGEIST['DATA_CACHE']
    inpath = os.path.join(cache_dir, 'contributions', 'contribs_by_zip.csv')

    with open(inpath) as infile:

        reader = csv.DictReader(infile)

        for record in reader:
            Contribution.objects.create(
                zipcode=record['substring'],
                total=record['amount'],
                republicans=record['republican_amount'],
                democrats=record['democratic_amount']
            )


def load(force=False):

    if force:
        reset()

    reset()  # reset anyway

    load_contributions()


if __name__ == '__main__':
    load()
