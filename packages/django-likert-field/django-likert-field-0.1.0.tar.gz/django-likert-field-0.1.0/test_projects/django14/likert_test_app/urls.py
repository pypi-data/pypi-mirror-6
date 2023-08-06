#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from .views import SurveyCreateView, SurveyDetailView, SurveyListView


urlpatterns = patterns('',
    url(r'^$', SurveyListView.as_view(), name='likert_list'),
    url(r'^add/', SurveyCreateView.as_view(), name="likert_add"),
    url(r'^added/$', TemplateView.as_view(template_name='likert/added.html'), name='likert_added'),
    url(r'^survey/(?P<pk>\w+)/$', SurveyDetailView.as_view(), name='likert_detail'),
)
