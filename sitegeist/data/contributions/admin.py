from django.contrib import admin

from sitegeist.data.contributions.models import Contribution


class ContributionAdmin(admin.ModelAdmin):
    list_display = ('zipcode', 'total', 'democrats', 'republicans')
admin.site.register(Contribution, ContributionAdmin)
