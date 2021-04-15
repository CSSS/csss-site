from django.conf.urls import url

from .views.Constants import ENDPOINT_MODIFY_VIA_WEBFORM, \
    ENDPOINT_MODIFY_VIA_JSON, ENDPOINT_DELETE_ELECTION
from .views.endpoints.delete_selected_election import delete_selected_election
from .views.endpoints.election_page import get_nominees
from .views.endpoints.json.create_election_json import display_and_process_html_for_new_json_election
from .views.endpoints.json.display_and_process_html_for_json import \
    display_and_process_html_for_modification_of_json_election
from .views.endpoints.list_of_elections import list_of_elections
from .views.endpoints.webform.create_election_webform import \
    display_and_process_html_for_new_webform_election
from .views.endpoints.webform.display_and_process_html_for_webform import \
    display_and_process_html_for_modification_of_webform_election

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
        fr'^{ENDPOINT_MODIFY_VIA_JSON}/$',
        display_and_process_html_for_modification_of_json_election,
        name='Show Page to Update Election'
    ),
    url(
        fr'^{ENDPOINT_MODIFY_VIA_WEBFORM}/$',
        display_and_process_html_for_modification_of_webform_election,
        name='Show Page to Update Election'
    ),
    url(
        fr'^{ENDPOINT_DELETE_ELECTION}/$',
        delete_selected_election,
        name="Delete Selected Election"
    ),
    url(r'^(?P<slug>[-\w]+)/$', get_nominees, name='nominees_in_nominationPage'),
    url(r'^$', list_of_elections, name="index"),

]
