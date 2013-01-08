import os
import sys

from sitegeist.data.census import loading as census_loading
from sitegeist.data.epa import loading as epa_loading
from sitegeist.data.locations import loading as locations_loading
from sitegeist.data.schools import loading as schools_loading
from sitegeist.data import conf

SOURCES = {
    "census": census_loading,
    "epa": epa_loading,
    "locations": locations_loading,
    "schools": schools_loading,
}

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Load Sitegeist data sources")

    parser.add_argument("sources", metavar="SOURCES", nargs="+",
                       help="one or more source: %s" % ", ".join(sorted(SOURCES.keys())))

    parser.add_argument("-c", "--config", dest="config", metavar='PATH',
                       help="path to config file")
    parser.add_argument("-d", "--dryrun", dest="dryrun", action="store_true",
                       help="load data source, but do not save to database")

    args = parser.parse_args()

    if args.config:
        path = os.path.abspath(os.path.expandvars(os.path.expanduser(args.config)))
        conf.load_config(path)

    for source in args.sources:

        if source in SOURCES:
            mod = SOURCES[source]
            try:
                mod.load()
            except Exception, e:
                sys.stderr.write("Could not load %s\n\t%s" % (source, e))
