from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list_of_officers$', views.list_of_officers, name='list_of_officers'),
    url(r'^input_exec_info$', views.input_exec_info, name='Add an Exec'),
    url(r'^process_exec_info$', views.process_exec_info, name='Add an Exec'),
    url(r'^who_we_are$', views.index, name='index'),
    url(r'^bad_passphrase$', views.bad_passphrase, name='index'),
]
