from django.conf.urls import url

from elections.views.endpoints.json.create_election_json import display_and_process_html_for_new_json_election
from elections.views.endpoints.json.display_and_process_html_for_json import \
    display_and_process_html_for_modification_of_json_election
from elections.views.endpoints.webform.create_election_webform import display_and_process_html_for_new_webform_election
from elections.views.endpoints.webform.display_and_process_html_for_webform import \
    display_and_process_html_for_modification_of_webform_election
from .views.endpoints.delete_selected_election import delete_selected_election
from .views.endpoints.display_choices_for_updating_elections import show_page_where_user_can_select_election_to_update
from .views.endpoints.election_page import get_nominees
from .views.endpoints.list_of_elections import list_of_elections
from .views.endpoints.process_user_election_action import determine_election_action

urlpatterns = [
    url(
        r'^new_election_json/$',
        display_and_process_html_for_new_json_election,
        name='Show Page To Create Election'
    ),
    url(
        r'^new_election_webform/$',
        display_and_process_html_for_new_webform_election,
        name="Show Page To Create Election"
    ),

    url(
        r'^election_modification_json/$',
        display_and_process_html_for_modification_of_json_election,
        name='Show Page to Update Election'
    ),
    url(
        r'^election_modification_webform/$',
        display_and_process_html_for_modification_of_webform_election,
        name='Show Page to Update Election'
    ),

    url(
        r'^show_options_for_election_updating/$',
        show_page_where_user_can_select_election_to_update,
        name="Select Election To Modify"
    ),
    url(
        r'^process_option_for_election_updating/$',
        determine_election_action,
        name="Determine Election Action"
    ),
    url(
        r'^delete/$',
        delete_selected_election,
        name="Delete Selected Election"
    ),
    url(r'^(?P<slug>[-\w]+)/$', get_nominees, name='nominees_in_nominationPage'),
    url(r'^$', list_of_elections, name="index"),

]
