from django.conf.urls import url

from events.workshops import views

urlpatterns = [
    url(r'$', views.workshops, name='workshops')
]
