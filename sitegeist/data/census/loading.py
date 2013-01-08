import csv
import os
import time

from django.conf import settings
import census
import us

from sitegeist.data.census import DATA
from sitegeist.data.census.models import Tract


def _chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def reset():
    Tract.objects.all().delete()


def load_tracts():

    cache_dir = settings.SITEGEIST['DATA_CACHE']
    tracts_path = os.path.join(cache_dir, 'locations', 'tracts.csv')

    with open(tracts_path) as infile:

        reader = csv.DictReader(infile)

        for record in reader:

            Tract.objects.create(
                state=record['state'],
                county=record['county'],
                tract=record['tract'],
            )


def load_tract_records(keys):

    """




        Need to reload Montana!!!!!!!!

        for state in [us.states.MT, ]:

    """

    c = census.Census(settings.CENSUS_KEY)

    # for state in [us.states.MT]:
    for state in us.STATES:

        print state.name

        counties = Tract.objects.filter(state=state.fips).values_list('county', flat=True)

        for county in sorted(set(counties)):

            print "\t%s" % county

            for chunk in _chunks(keys, 5):

                fields = ",".join(chunk)

                res = c.acs.state_county_tract(fields, state.fips, county, census.ALL)
                for record in res:

                    tract = record.pop('tract')
                    del record['state']
                    del record['county']

                    for k in record:
                        if record[k] == 'null':
                            record[k] = None

                    qs = Tract.objects.filter(state=state.fips, county=county, tract=tract)
                    qs.update(**record)

            time.sleep(1)

        time.sleep(5)


def load():
    # reset()
    # load_tracts()
    # load_tract_records(DATA.keys())

    keys = ["B25035_001E"]
    load_tract_records(keys)

if __name__ == '__main__':
    load()
