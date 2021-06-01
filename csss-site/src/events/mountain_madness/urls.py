from django.conf.urls import url

from events.mountain_madness import views

urlpatterns = [
    url(r'^2021$', views.mm2021, name='mountain_madness2021'),
    url(r'^2020$', views.mm2020, name='mountain_madness2020'),
    url(r'^2019$', views.mm2019, name='mountain_madness2019'),
]
