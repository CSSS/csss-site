from django.conf.urls import url

from events.views import mm

urlpatterns = [
    url(r'^mm/2019$', mm.mm2019, name='mountain_madness2019'),
    url(r'^mm/2020$', mm.mm2020, name='mountain_madness2020'),
    url(r'^mm/2021$', mm.mm2021, name='mountain_madness2021'),
]
