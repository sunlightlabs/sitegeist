import csv
import datetime
import os
import zipfile

from django.conf import settings
from django.core.management import setup_environ
import boundaries
import census
import requests
import us

from sitegeist.data.conf import settings
from sitegeist import settings as django_settings

setup_environ(django_settings)


def _dl_path():
    return os.path.join(settings['cache_dir'], 'locations', 'tracts')


def name_func(state, field):
    import boundaries

    def inner(feature):
        name = "%s %s" % (state, feature.get(field))
        return boundaries._clean_string(name)
    return inner


def slug_func(field):
    import boundaries

    def inner(feature):
        slug = "%s-%s" % (feature.get(field), feature.get('GEOID10'))
        return boundaries._clean_string(slug)
    return inner


def label_point_func(feature):
    from django.contrib.gis.geos import point
    from django.contrib.gis.gdal.geometries import MultiPolygon

    def avg(items):
        return sum(items) / len(items)

    geom = feature.feature.geom
    if isinstance(geom, MultiPolygon):
        coords = [g.centroid.coords for g in geom]
        lat = avg(list(c[0] for c in coords))
        lon = avg(list(c[1] for c in coords))
        label_point = (lat, lon)
    else:
        label_point = geom.centroid.coords
    return point.Point(*label_point)


def reset():
    pass


def load_tracts():

    c = census.Census(settings.CENSUS_KEY)

    with open('tracts.csv', 'w') as outfile:

        writer = csv.writer(outfile)
        writer.writerow(('state', 'county', 'tract', 'name'))

        for state in us.STATES:

            print state.name

            for cr in c.sf1.state_county('NAME', state.fips, census.ALL):
                for tr in c.sf1.state_county_tract('NAME', state.fips, cr['county'], census.ALL):
                    record = (state.fips, cr['county'], tr['tract'], tr['NAME'])
                    writer.writerow(record)


def load_zcta_boundaries():

    # clear registry
    boundaries.registry = {}

    dl_path = _dl_path()
    today = datetime.date.today()

    for state in us.STATES:

        print state.name

        url = state.shapefile_urls('zcta')
        filename = url.split('/')[-1]
        (name, ext) = filename.rsplit('.', 1)

        extract_path = os.path.join(dl_path, name)
        if not os.path.exists(extract_path):

            os.mkdir(extract_path)

            zip_path = os.path.join(dl_path, filename)
            if not os.path.exists(zip_path):
                resp = requests.get(url)
                with open(zip_path, 'w') as outfile:
                    outfile.write(resp.content)

            with zipfile.ZipFile(zip_path, 'r') as archive:
                archive.extractall(extract_path)

            os.unlink(zip_path)

        boundaries.register('%s-zcta' % state.name.lower().replace(' ', ''),
            singular='census-zcta',
            domain='US',
            file=extract_path,
            last_updated=today,
            name_func=name_func(state.name, 'ZCTA5CE10'),
            id_func=boundaries.attr('ZCTA5CE10'),
            slug_func=slug_func('ZCTA5CE10'),
            label_point_func=label_point_func,
            authority='United States Census Bureau',
            source_url='http://www.census.gov/cgi-bin/geo/shapefiles2010/main',
            data_url=url,
        )

    from django.core import management
    management.call_command('loadshapefiles')


def load_tract_boundaries():

    # clear registry
    boundaries.registry = {}

    dl_path = _dl_path()
    today = datetime.date.today()

    for state in us.STATES:

        print state.name

        url = state.shapefile_urls('tract')
        filename = url.split('/')[-1]
        (name, ext) = filename.rsplit('.', 1)

        extract_path = os.path.join(dl_path, name)
        if not os.path.exists(extract_path):

            os.mkdir(extract_path)

            zip_path = os.path.join(dl_path, filename)
            if not os.path.exists(zip_path):
                resp = requests.get(url)
                with open(zip_path, 'w') as outfile:
                    outfile.write(resp.content)

            with zipfile.ZipFile(zip_path, 'r') as archive:
                archive.extractall(extract_path)

            os.unlink(zip_path)

        boundaries.register('%s-census' % state.name.lower().replace(' ', ''),
            singular='census-tract',
            domain='US',
            file=extract_path,
            last_updated=today,
            name_func=name_func(state.name, 'NAMELSAD10'),
            id_func=boundaries.attr('TRACTCE10'),
            slug_func=slug_func('NAMELSAD10'),
            label_point_func=label_point_func,
            authority='United States Census Bureau',
            source_url='http://www.census.gov/cgi-bin/geo/shapefiles2010/main',
            data_url=url,
        )

    from django.core import management
    management.call_command('loadshapefiles')


def load(force=False):

    if force:
        reset()

    # load_tracts()
    # load_tract_boundaries()

    # load_zctas()
    load_zcta_boundaries()

if __name__ == '__main__':
    load()
