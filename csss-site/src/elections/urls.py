from django.conf.urls import url

from .views import election_management
<<<<<<< HEAD
from .views import list_nominees

urlpatterns = [
    url(r'^create/$', election_management.create_specified_election, name='create_election'),
    url(
        r'^create_or_update_json/$',
        election_management.create_or_update_specified_election_with_provided_json,
        name='update_election_json'
    ),
    url(r'^select_election/$', election_management.select_election_to_update, name='select_election'),
    url(
        r'^determine_election_action/$',
        election_management.determine_election_action,
        name='determine_election_action'
    ),
    url(r'^update/$', election_management.update_specified_election, name='update_election'),
    url(r'^(?P<slug>[-\w]+)/$', list_nominees.get_nominees, name='nominees_in_nominationPage'),
=======

urlpatterns = [
    url(
        r'^show_create_webform/$',
        election_management.show_page_for_user_to_enter_new_election_information_from_webform,
        name='Show Page To Create Election'
    ),
    url(
        r'^show_create_json/$',
        election_management.show_page_for_user_to_enter_new_election_information_from_json,
        name='Show Page To Create Election'
    ),
    url(
        r'^create_webform/$',
        election_management.process_new_election_information_from_webform,
        name='Process User Input For New Election'
    ),
    url(
        r'^create_json/$',
        election_management.process_new_election_information_from_json,
        name='Process User Input For New Election'
    ),
    url(
        r'^select_election_to_update/$',
        election_management.show_page_where_user_can_select_election_to_update,
        name="Select Election To Modify"
    ),
    url(
        r'^determine_election_action/$',
        election_management.determine_election_action,
        name="Determine Election Action"
    ),
    url(
        r'^show_update_json/$',
        election_management.show_page_for_user_to_modify_election_information_from_json,
        name='Show Page to Update Election'
    ),
    url(
        r'^update_json/$',
        election_management.process_existing_election_information_from_json,
        name='Process User Input for Existing Election'
    ),
    url(
        r'^show_update_webform/$',
        election_management.show_page_for_user_to_modify_election_information_from_webform,
        name='Show Page to Update Election'
    ),
    url(
        r'^update_webform/$',
        election_management.process_existing_election_information_from_webform,
        name='Process User Input for Existing Election'
    ),
    url(
        r'^delete/$',
        election_management.delete_selected_election,
        name="Delete Selected Election"
    ),
    url(r'^(?P<slug>[-\w]+)/$', election_management.get_nominees, name='nominees_in_nominationPage'),
    url(r'^$', election_management.list_of_elections, name="index"),

>>>>>>> 9d3e62ef5c2b5ac2e16725ca7c6384c7c86b2e26
]
