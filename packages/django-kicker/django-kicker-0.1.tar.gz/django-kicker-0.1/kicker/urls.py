from django.conf.urls import patterns, include, url
from kicker.views import Dispatch

urlpatterns = patterns('',
        url(r'^(?P<model>\w+)/(?P<timestamp>\d+?\.\d+?)/$', Dispatch.as_view()),
)

