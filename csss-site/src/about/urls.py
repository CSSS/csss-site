from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list_of_officers$', views.list_of_officers, name='list_of_officers'),
    url(r'^input_officer_info$', views.input_officer_info, name='Add an Officer'),
    url(r'^process_officer_info$', views.process_officer_info, name='Add an Officer'),
    url(r'^who_we_are$', views.index, name='index'),
    url(r'^bad_passphrase$', views.bad_passphrase, name='index'),
]
