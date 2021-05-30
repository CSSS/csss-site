from django.conf.urls import url

from events.views import mm

urlpatterns = [
    url(r'^mountain_madness2019$', mm.mountain_madness2019, name='mountain_madness2019'),
    url(r'^mountain_madness2020$', mm.mountain_madness2020, name='mountain_madness2020'),
    url(r'^mountain_madness2021$', mm.mountain_madness2021, name='mountain_madness2021'),
]
