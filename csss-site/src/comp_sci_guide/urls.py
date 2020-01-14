from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^software$', views.software, name='software'),
    url(r'^textbooks$', views.textbooks, name='textbooks'),
    url(r'^course_reviews$', views.course_review, name='course_review'),
    url(r'^$', views.index, name='index'),
]
