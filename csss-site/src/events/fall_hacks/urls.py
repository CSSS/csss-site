from django.conf.urls import url

from events.fall_hacks import views

urlpatterns = [
    url(r'^2020$', views.fall_hacks2020, name='fall_hacks2020'),
    url(r'^2020/submissions$', views.fall_hacks_submissions2020, name='fall_hacks_submissions2020'),
]
