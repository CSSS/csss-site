from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/$', views.get_nominees, name='nominees_in_nominationPage'),
]
