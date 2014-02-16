from django.conf.urls import patterns, url
from views import show_feed

urlpatterns = patterns('',
    url(r'^(\w+).xml', show_feed, name="fulltextfeed_show"),
)
