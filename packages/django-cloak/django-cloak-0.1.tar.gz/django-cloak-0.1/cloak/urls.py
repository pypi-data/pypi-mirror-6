from django.conf.urls import patterns, url
from .views import cloak, uncloak, login

urlpatterns = patterns('',
    url(r'^cloak/(?P<pk>.*)$', cloak),
    url(r'^uncloak$', uncloak),
    url(r'^login/(?P<signature>.*)$', login),
)
