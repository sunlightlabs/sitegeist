from django.core.management.base import BaseCommand, CommandError
from django.utils.importlib import import_module


class Command(BaseCommand):

    def handle(self, *args, **options):

        if not args:
            raise CommandError("at least one source is required")

        for source in args:

            try:

                loading = import_module("sitegeist.data.%s.loading" % source)
                loading.load()

            except ImportError:
                raise CommandError("%s is not a valid source" % source)
