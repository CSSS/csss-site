from django.conf.urls import url

from events.tech_fair import views

urlpatterns = [
    url(r'^2022$', views.tech_fair2022, name='tech_fair2022'),
    url(r'^2022/main$', views.tech_fair2022_main, name='tech_fair2022_main'),
]
