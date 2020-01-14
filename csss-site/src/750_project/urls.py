from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^dev_tools$', views.dev_tools, name='dev_tools'),
    url(r'^hacktime$', views.hacktime, name='hacktime'),
    url(r'^workshops$', views.workshops, name='workshops'),
    url(r'^$', views.index, name='index'),
]
