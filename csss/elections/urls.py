from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/$', views.NomineeListView.as_view(), name='nominees_in_nominationPage'),
    url(r'^([-\w]+)/(?P<slug>[-\w]+)/$', views.NomineeDetailView.as_view(), name='nominee'),
]