from django.conf.urls import url

from events.mountain_madness import views

urlpatterns = [
    url(r'^2023$', views.mm2023, name='mountain_madness2023'),
    url(r'^2022$', views.mm2022, name='mountain_madness2022'),
    url(r'^2021/submissions$', views.mm2021_submissions, name='mountain_madness2021_submissions'),
    url(r'^2021$', views.mm2021, name='mountain_madness2021'),
    url(r'^2020$', views.mm2020, name='mountain_madness2020'),
    url(r'^2019$', views.mm2019, name='mountain_madness2019'),
]
