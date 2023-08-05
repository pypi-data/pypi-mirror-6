'''
Example urls

from django.conf.urls import patterns, url
from multisessionform.views import MultiSessionFormView

urlpatterns = patterns('',
    url(r'^$', MultiSessionFormView.as_view()),
    url(r'^(?P<pk>\d+)/$', MultiSessionFormView.as_view()),
    url(r'^(?P<pk>\d+)/(?P<form_field>[\w-]+)/$', MultiSessionFormView.as_view()),
)
'''