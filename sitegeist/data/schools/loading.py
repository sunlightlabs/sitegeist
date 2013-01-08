import csv
import os
import zipfile

from django.conf import settings
import requests

from sitegeist.data.schools.models import School

DATA_URL = "http://nces.ed.gov/ccd/data/zip/sc091a_csv.zip"


def load():

    filename = DATA_URL.split('/')[-1]
    dir_name = filename.split('.')[0]

    dl_path = os.path.join(settings.SITEGEIST['DATA_CACHE'], 'schools')
    extract_path = os.path.join(dl_path, dir_name)
    zip_path = os.path.join(dl_path, filename)

    if not os.path.exists(dl_path):
        os.mkdir(dl_path)

    if not os.path.exists(extract_path):

        if not os.path.exists(zip_path):
            with open(zip_path, 'w') as outfile:
                resp = requests.get(DATA_URL)
                outfile.write(resp.content)

        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(extract_path)

    School.objects.all().delete()

    for csv_filename in os.listdir(extract_path):

        csv_path = os.path.join(extract_path, csv_filename)

        with open(csv_path) as infile:

            print csv_path

            reader = csv.DictReader(infile)
            for record in reader:

                params = {
                    'nces_id': record['ncessch'],
                    'name': record['schnam09'],
                    'street': record['mstree09'],
                    'city': record['mcity09'],
                    'state': record['mstate09'],
                    'zipcode': record['mzip09'],
                    'enrollment': record['member09'],
                    'locale_code': record['ulocal09'],
                    'type_code': record['type09'],
                    'level_code': record['level09'],
                    'level_low': record['gslo09'],
                    'level_high': record['gshi09'],
                    'status': record['status09'],
                }

                School.objects.create(**params)


if __name__ == "__main__":
    load()
