"""URLs for the dated_values app."""
from django.conf.urls.defaults import patterns, url

from .views import ValuesManagementView


urlpatterns = patterns(
    '',
    url(r'^(?P<ctype_id>\d+)/(?P<object_id>\d+)/$',
        ValuesManagementView.as_view(), name='dated_values_management_view'),
)
