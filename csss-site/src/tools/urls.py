from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^sample_tool/$', views.sample_tool),
]
