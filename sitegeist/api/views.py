from collections import defaultdict
import datetime
import json
import logging
import re

from boundaries.models import Boundary
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from sitegeist.data.census.models import Tract
from sitegeist.data.contributions.models import Contribution
from sitegeist.data.epa.models import Site
from sitegeist.data.nhgis.models import Tract as NHGISTract
from sitegeist.data import darksky, foursquare, wunderground, yelp
from sitegeist.cache import CoordinateCache
from sitegeist.formatting import dec2num, dec2pct, dec2curr
from sitegeist import utils, viz

RESPONSE_MIMETYPES = {
    'text/html': 'html',
    'application/json': 'json',
}
DEFAULT_RESPONSE_MIMETYPE = 'application/json'
DEFAULT_CLL = ("38.906956", "-77.042883")

logger = logging.getLogger(__name__)
boundary_cache = CoordinateCache("boundaries")

LLFORMAT = re.compile(r"^(?P<lat>\-?\d+(\.\d+)?),(?P<lon>\-?\d+(\.\d+)?)$")


class Geo(defaultdict):

    def __init__(self, *args, **kwargs):
        super(Geo, self).__init__(list, *args, **kwargs)
        self.lat = None
        self.lon = None


class SitegeistView(View):

    namespace = None

    def __init__(self, *args, **kwargs):
        super(SitegeistView, self).__init__(*args, **kwargs)
        self._geocache = CoordinateCache("view-%s" % self.namespace)

    def load_data(self, request, coords, **args):
        """ Load the data dict needed by this view.
            Subclasses should implement this method.
        """
        raise NotImplementedError("subclass and implement load_data()")

    def get_template(self):
        return "sitegeist/panes/%s.html" % self.namespace

    def _base_response(self, coords):
        return {
            "geo": {
                "ll": [coords.lat, coords.lon],
                "boundaries": coords,
            },
            "data": {},
        }

    def _get_bounds(self, request, param='cll'):
        """ Get coordinates from the HTTP request.
            The only supported method is via lat and lon querystring params.
        """

        cll = request.GET.get(param)

        # set default of Sunlight offices
        lat = DEFAULT_CLL[0]
        lon = DEFAULT_CLL[1]

        if cll and LLFORMAT.match(cll):
            (lat, lon) = cll.split(',')

        coords = (lat, lon)
        bounds = boundary_cache.get(coords)

        if not bounds:

            bounds = Geo()
            bounds.lat = lat
            bounds.lon = lon

            pt = "POINT(%s %s)" % (lon, lat)

            for boundary in Boundary.objects.filter(shape__contains=pt):
                bounds[boundary.set_name].append(boundary.as_dict())

            if bounds:
                boundary_cache.set(coords, bounds)

        return bounds

    def _get_response_type(self, request):
        """ Get the type of response needed by the client.
            The only supported method for JSON (at this time) is via the
            HTTP_X_REQUESTED_WITH header with a value of XMLHttpRequest.
            I lied, you can also pass format=json as a query string param.
        """
        return 'json' if request.is_ajax() or request.GET.get('format') == 'json' else 'html'

    def get(self, request, **args):
        """ Process GET request. Defers to the subclass's load_data()
            method if cached data is not found.
        """

        # get values from response
        response_type = self._get_response_type(request)
        bounds = self._get_bounds(request)

        if bounds:

            coords = (float(bounds.lat), float(bounds.lon))

            logger.debug("attempting cache read width (%s, %s)" % coords)

            data = self._geocache.get(coords)

            if not data:  # if data is not cached, load it and cache it

                logger.debug("cache miss, calling load_data()")

                data = self.load_data(request, bounds, **args)
                self._geocache.set(coords, data)

            else:
                logger.debug("cache hit!!!!")

        else:
            coords = None
            data = {'data': {}}

        # response rendering

        if response_type == 'html':
            context = {
                'coords': coords,
                'data': data['data'],
                'vertical_offset': request.GET.get('vo'),
                'namespace': self.namespace,
                'show_header': request.GET.get('header') != "0",
            }
            return render(request, self.get_template(), context)

        return HttpResponse(json.dumps(data), content_type="application/json")


#
# subclasses
#

class PeopleView(SitegeistView):
    namespace = "people"

    def load_data(self, request, bounds, **args):

        resp = self._base_response(bounds)

        if "census-tract" in bounds:

            tract = bounds["census-tract"][0]
            results = Tract.objects.filter(
                state=tract['metadata']['STATEFP10'],
                county=tract['metadata']['COUNTYFP10'],
                tract=tract['metadata']['TRACTCE10'])

            if results:

                t = results[0]

                # ethnicity

                # top_ancestry = max(
                #     ((k, getattr(t, k, None)) for k in ("B04003_%03dE" % i for i in range(2, 108))),
                #     key=lambda x: x[1]
                # )

                # resp["data"].update({
                #     "ethnicity": {
                #         "total": dec2num(top_ancestry[1], whole=True),
                #         "pct": dec2pct(top_ancestry[1] / t.B04003_001E),
                #         "name": CENSUS_FIELDS[top_ancestry[0]],
                #     },
                # })

                # update avarage age in years, months

                (years, months) = utils.age2ym(t.B01002_001E)

                if years is not None and months is not None:

                    resp["data"].update({
                        "average_age": {
                            "years": years,
                            "months": months,
                        }
                    })

                # relative age distribution

                total = t.B01001_001E

                males = []
                females = []

                for i in range(3, 26):
                    males.append(getattr(t, "B01001_%03dE" % i))
                    females.append(getattr(t, "B01001_%03dE" % (i + 24)))

                total = max([max(males), max(females)])

                if total:

                    males = [dec2pct(m / total, whole=True) for m in males]
                    females = [dec2pct(f / total, whole=True) for f in females]

                    resp["data"].update({
                        "age_distribution": {
                            "female": females,
                            "male": males,
                        }
                    })

                # under five years of age

                if t.B11005_001E:

                    resp["data"].update({
                        "under_five": {
                            "total": dec2num(t.B01001_003E + t.B01001_027E, whole=True),
                            "per_household": dec2num((t.B01001_003E + t.B01001_027E) / t.B11005_001E),
                            "households": dec2num(t.B11005_001E, whole=True),
                        }
                    })

                # gender

                if t.B01001_001E:

                    resp["data"].update({
                        "gender": {
                            "male_pct": dec2pct(t.B01001_002E / t.B01001_001E),
                            "female_pct": dec2pct(t.B01001_026E / t.B01001_001E),
                        },
                    })

                # update rest of the stuff

                if t.B19001_001E:

                    resp["data"].update({
                        "average_household_income": {
                            "total": dec2curr(t.B19013_001E),
                            "pct_gt_100k": dec2pct((t.B19001_014E + t.B19001_015E + t.B19001_016E + t.B19001_017E) / t.B19001_001E),
                            "pct_60k_100k": dec2pct((t.B19001_012E + t.B19001_013E) / t.B19001_001E),
                            "pct_30k_60k": dec2pct((t.B19001_007E + t.B19001_008E + t.B19001_009E + t.B19001_010E + t.B19001_011E) / t.B19001_001E),
                            "pct_10k_30k": dec2pct((t.B19001_003E + t.B19001_004E + t.B19001_005E + t.B19001_006E) / t.B19001_001E),
                            "pct_lt_10k": dec2pct((t.B19001_002E) / t.B19001_001E),
                        },
                    })

        if "census-zcta" in bounds:

            zcta = bounds["census-zcta"][0]

            try:

                c = Contribution.objects.get(zipcode=zcta['metadata']['ZCTA5CE10'])

                total = c.democrats + c.republicans

                resp['data'].update({
                    "contributions": {
                        "r": dec2curr(c.republicans, whole=True),
                        "r_pct": dec2pct(c.republicans / total),
                        "r_raw": int(c.republicans),
                        "d": dec2curr(c.democrats, whole=True),
                        "d_pct": dec2pct(c.democrats / total),
                        "d_raw": int(c.democrats),
                    },
                })

            except:
                pass  # eh, don't really care

        return resp


class HousingView(SitegeistView):
    namespace = "housing"

    def load_data(self, request, bounds, **args):

        resp = self._base_response(bounds)

        if "census-tract" in bounds:

            tract = bounds["census-tract"][0]
            results = Tract.objects.filter(
                state=tract['metadata']['STATEFP10'],
                county=tract['metadata']['COUNTYFP10'],
                tract=tract['metadata']['TRACTCE10'])

            if results:

                t = results[0]

                # median value

                if t.B25077_001E:

                    resp["data"].update({
                        "owned": {
                            "median_value": dec2curr(t.B25077_001E, whole=True),
                        }
                    })

                # rental pct

                try:

                    rental_pct = t.B25003_003E / (t.B25003_002E + t.B25003_003E)

                    resp["data"].update({
                        "rentals": {
                            "median_cost": dec2curr(t.B25058_001E, whole=True),
                            "pct": dec2pct(rental_pct, whole=True),
                            "svg": viz.svg_piechart(rental_pct, 50, 50, 35)
                        }
                    })

                except:
                    pass

                # transportation

                trans_total = t.B08301_001E

                if trans_total:

                    resp["data"].update({
                        "transport": {
                            "total": dec2num(trans_total, whole=True),
                            "auto_pct": dec2num((t.B08301_002E / trans_total) * 100, whole=True),
                            "public_pct": dec2num((t.B08301_010E / trans_total) * 100, whole=True),
                            "bike_pct": dec2num((t.B08301_018E / trans_total) * 100, whole=True),
                            "walk_pct": dec2num((t.B08301_019E / trans_total) * 100, whole=True),
                        }
                    })

        # resp['data']['alert'] = "New housing data is being loaded from the Census Bureau. Please excuse our dust."

        return resp


class FunView(SitegeistView):
    namespace = "fun"

    def load_data(self, request, bounds, **args):

        resp = self._base_response(bounds)

        # recommended places

        yelp_results = yelp.nearby(bounds.lat, bounds.lon, categories=yelp.BASE_CATEGORIES)

        places = []
        for place in yelp_results[:3]:

            data = {
                "id": place.get("id"),
                "name": place.get("name"),
                "rating": place.get("rating"),
                "categories": [c[0] for c in place.get("categories", [])],
                "url": place.get("url"),
                "mobile_url": place.get("mobile_url"),
                "rating_url": place.get("rating_img_url"),
                "image_url": place.get("image_url"),
                "reviews": place.get("review_count"),
            }

            if "location" in place:
                data["address"] = ", ".join(place["location"].get("address", []))

            places.append(data)

        if places:
            resp["data"].update({
                "recommended": places,
            })

        # local theaters

        theaters = foursquare.search(bounds.lat, bounds.lon, foursquare.MOVIE_THEATERS)
        if theaters:
            resp["data"]["theaters"] = theaters

        # localflavor

        a_bit_further = yelp.METERS_PER_MILE * 5
        yelp_results = yelp.nearby(bounds.lat, bounds.lon, categories='localflavor', radius=a_bit_further)

        places = []
        for place in yelp_results[:10]:

            if "yelp" not in place.get("name", "").lower():

                data = {
                    "id": place.get("id"),
                    "name": place.get("name"),
                    "rating": place.get("rating"),
                    "categories": [c[0] for c in place.get("categories", [])],
                    "url": place.get("url"),
                    "mobile_url": place.get("mobile_url"),
                    "rating_url": place.get("rating_img_url"),
                    "image_url": place.get("image_url"),
                    "reviews": place.get("review_count"),
                }

                if "location" in place:
                    data["address"] = ", ".join(place["location"].get("address", []))

                places.append(data)

        if places:
            resp["data"].update({
                "localflavor": places[:5],
            })

        # foursquare

        fsqr = foursquare.explore(bounds.lat, bounds.lon)

        if fsqr:
            resp["data"]["foursquare"] = fsqr

        return resp


class EnvironmentView(SitegeistView):
    namespace = "environment"

    def load_data(self, request, bounds, **args):

        resp = self._base_response(bounds)

        # contaminated

        pnt = fromstr('POINT(%s %s)' % (bounds.lon, bounds.lat), srid=4326)
        qs = Site.objects.filter(point__distance_lte=(pnt, D(mi=5)))
        sites = sorted(qs.distance(pnt), cmp=lambda x, y: cmp(x.distance, y.distance))

        if sites:

            resp['data'].update({
                "contaminated": {
                    "distance": "%.1f" % sites[0].distance.mi,
                    "url": sites[0].url,
                }
            })

        # Dark Sky

        ds = darksky.forecast(bounds.lat, bounds.lon)

        if 'hourSummary' in ds:

            forecast = ds['hourSummary'].lower()

            if forecast == 'clear':
                ds['forecast_code'] = 'sun'
            elif 'sprinkling' in forecast:
                ds['forecast_code'] = 'rain'
            elif 'sleet' in forecast:
                ds['forecast_code'] = 'sleet'
            elif 'sun' in forecast:
                ds['forecast_code'] = 'sun'
            elif 'rain' in forecast:
                ds['forecast_code'] = 'rain'
            elif 'cloud' in forecast:
                ds['forecast_code'] = 'cloud'

        resp['data']['darksky'] = ds

        # Wunderground

        resp['data']['wunderground'] = wunderground.almanac(bounds.lat, bounds.lon)

        return resp


class HistoryView(SitegeistView):
    namespace = "history"

    def load_data(self, request, bounds, **args):

        resp = self._base_response(bounds)
        resp['data'] = {}

        if "census-tract" in bounds:

            tract = bounds["census-tract"][0]

            # nhgis
            results = NHGISTract.objects.filter(
                state=tract['metadata']['STATEFP10'],
                county=tract['metadata']['COUNTYFP10'],
                tract=tract['metadata']['TRACTCE10'])

            if results:

                years = {
                    '1970': None,
                    '1980': None,
                    '1990': None,
                    '2000': None,
                    '2010': None,
                }

                for res in results:
                    years[res.year] = res.units

                housing_data = {
                    'current': dec2num(years['2010'], whole=True),
                    'current_before': ("%i" % (years['2010'] - 1))[-1],
                    'current_after': ("%i" % (years['2010'] + 1))[-1],
                    'history': years,
                }

                if len([v for v in years.values() if v]) > 2:
                    housing_data['history_svg'] = viz.svg_housinghistory(years)

                resp['data'].update({
                    'housing': housing_data,
                })

            # census

            results = Tract.objects.filter(
                state=tract['metadata']['STATEFP10'],
                county=tract['metadata']['COUNTYFP10'],
                tract=tract['metadata']['TRACTCE10'])

            if results:

                t = results[0]

                if t.B25035_001E:

                    thisyear = datetime.datetime.utcnow().year

                    resp['data'].update({
                        'median_year': "%d" % t.B25035_001E,
                        'median_home_age': "%d" % (thisyear - t.B25035_001E),
                    })

        return resp
