from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

# from TeacherRating import views
from questionnaire import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^event_overview/(?P<event_id>[0-9]+)$', views.event_overview, name='event_overview'),
    url(r'^event_detail/(?P<event_id>[0-9]+)/(?P<classification>[0-9])/(?P<main_id>[0-9]+)$', views.event_detail, name='event_detail'),
    url(r'^create_result$', views.create_result, name='create_result'),
]