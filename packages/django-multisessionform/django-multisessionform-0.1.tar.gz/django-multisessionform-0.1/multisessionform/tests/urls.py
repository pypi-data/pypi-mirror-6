from django.conf.urls import patterns, url
from multisessionform.views import MultiSessionFormView
from multisessionform.tests.models import MSFExample
from django.db.models import BooleanField

urlpatterns = patterns('',
    url(r'^noform/$', MultiSessionFormView.as_view()),
    url(r'^notemplate/$', MultiSessionFormView.as_view(form_class = MSFExample)),
    url(r'^notmixin/$', MultiSessionFormView.as_view(form_class = BooleanField, template_name = 'multisessionform/default_template.html')),
    url(r'^test/$', MultiSessionFormView.as_view(form_class = MSFExample, template_name = 'multisessionform/default_template.html')),
    url(r'^test/(?P<pk>\d+)/$', MultiSessionFormView.as_view(form_class = MSFExample, template_name = 'multisessionform/default_template.html')),
    url(r'^test/(?P<pk>\d+)/(?P<form_field>[\w-]+)/$', MultiSessionFormView.as_view(form_class = MSFExample, template_name = 'multisessionform/default_template.html')),
)