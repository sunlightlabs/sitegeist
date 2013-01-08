# Sitegeist

*Understand and uncover the identity of your location with a tap.*

Sitegeist is a mobile application that helps you to learn more about
your surroundings in seconds. Drawing on publicly available information,
the app presents solid data in a simple at-a-glance format to help you
tap into the pulse of your location. From demographics about people and
housing to the latest popular spots or weather, Sitegeist presents
localized information visually so you can get back to enjoying the
neighborhood. The application draws on free APIs such as the U.S.
Census, Yelp! and others to showcase what's possible with access to
data. Sitegeist was created by the Sunlight Foundation in consultation
with design firm IDEO and with support from the John S. and James L.
Knight Foundation. It is the third in a series of National Data Apps.


## Requirements

Python requirements in requirements.txt

Databases:

* PostgreSQL (with PostGIS)
* MongoDB


## Installation and Configuration

1. Install requirements using pip

        $ pip install -r requirements.txt

1. Create local settings file and edit.

        $ cp sitegeist/settings/dev.py sitegeist/settings/local.py
        $ vi sitegeist/settings/local.py

1. Create database structure.

        $ python manage.py syncdb
        $ python manage.py migrate

1. Configure mongodb indexes:

        $ python manage.py shell
        >>> from sitegeist import mongo
        >>> mongo.create_indexes()

1. Run Sitegeist

        python manage.py runserver


## Loading Data

Varies by data source. Check code to see how it works.

A general loading script was created, but the specifics of how it works
changes with each source. Know what happens before you use it.

    $ export DJANGO_SETTINGS_MODULE=sitegeist.settings
    $ ./bin/load -h
    usage: load.py [-h] [-c PATH] [-d] SOURCES [SOURCES ...]

    Load Sitegeist data sources

    positional arguments:
      SOURCES               one or more source: census, epa, locations, schools

    optional arguments:
      -h, --help            show this help message and exit
      -c PATH, --config PATH
                            path to config file
      -d, --dryrun          load data source, but do not save to database

