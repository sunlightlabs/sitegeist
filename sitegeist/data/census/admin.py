from django.contrib import admin
from sitegeist.data.census.models import Tract

class TractAdmin(admin.ModelAdmin):
    list_display = ('tract', 'county', 'state')

admin.site.register(Tract, TractAdmin)