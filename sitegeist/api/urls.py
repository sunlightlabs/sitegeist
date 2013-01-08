from django.conf.urls import patterns, url
from sitegeist.api.views import PeopleView, HousingView, FunView, EnvironmentView, HistoryView

urlpatterns = patterns('',
    url(r'^people/$', PeopleView.as_view()),
    url(r'^housing/$', HousingView.as_view()),
    url(r'^fun/$', FunView.as_view()),
    url(r'^environment/$', EnvironmentView.as_view()),
    url(r'^history/$', HistoryView.as_view()),
)
