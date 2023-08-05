from django.conf.urls import patterns
from django.conf.urls import url

from robots_txt.views import RobotsTextView

urlpatterns = patterns('',
    url(
        r'^robots.txt$',
        RobotsTextView.as_view(),
    ),
)
