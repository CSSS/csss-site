from django.conf.urls import url

from . import views
from administration.views import officer_views

urlpatterns = [
    url(r'^list_of_officers$', views.list_of_officers, name='list_of_officers'),
    url(r'^allow_officer_to_choose_name$', officer_views.allow_officer_to_choose_name, name='Add an Exec'),
    url(r'^display_page_for_officer_to_input_info$', officer_views.display_page_for_officers_to_input_their_info,
        name='Add an Exec'),
    url(r'^input_officer_info$', officer_views.process_information_entered_by_officer, name='Add an Exec'),
    url(r'^who_we_are$', views.index, name='index'),
    url(r'^bad_passphrase$', views.bad_passphrase, name='index'),
]
