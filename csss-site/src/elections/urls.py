from django.conf.urls import url

from .views.Constants import ENDPOINT_MODIFY_VIA_JSON, ENDPOINT_MODIFY_VIA_WEBFORM, \
    ENDPOINT_MODIFY_VIA_NOMINEE_LINKS, ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK, \
    ENDPOINT_CREATE_OR_UPDATE_NOMINEE_FOR_NOMINEE_VIA_PASSPHRASE__NOMINEE_LINK, ENDPOINT_DELETE_NOMINEE_LINKS
from .views.endpoints.delete_selected_election import delete_selected_election
from .views.endpoints.delete_selected_election_nominee_links import delete_selected_election__nominee_links
from .views.endpoints.election_page import get_nominees
from .views.endpoints.json.create_election_json import display_and_process_html_for_new_json_election
from .views.endpoints.json.display_and_process_html_for_json import \
    display_and_process_html_for_modification_of_json_election
from .views.endpoints.list_of_elections import list_of_elections
from .views.endpoints.nominee_links.create_election_nominee_links import \
    display_and_process_html_for_new_nominee_links_election
from .views.endpoints.nominee_links.display_and_process_html_for_nominee_links import \
    display_and_process_html_for_modification_of_election_and_nominee_links__nominee_links
from .views.endpoints.nominee_links.display_and_process_html_for_nominee_modification__nominee_link import \
    display_and_process_html_for_nominee_modification
from .views.endpoints.nominee_links.display_and_process_html_for_nominee_modification_via_passphrase__nominee_link \
    import display_and_process_html_for_nominee_modification_via_passphrase
from .views.endpoints.webform.create_election_webform import \
    display_and_process_html_for_new_webform_election
from .views.endpoints.webform.display_and_process_html_for_webform import \
    display_and_process_html_for_modification_of_webform_election
from .views.update_social_media_links import update_social_media_links

# https://docs.python.org/3/library/re.html#module-re
ELECTION_SLUG_PATTERN = r'(?P<slug>[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z_]+)'

# https://assertible.com/blog/7-http-methods-every-web-developer-should-know-and-how-to-test-them

urlpatterns = [
    url(r'^$', list_of_elections, name="List of Elections"),
    url(
        r'^new_election_json/$', display_and_process_html_for_new_json_election,
        name='Show Page To Create Election via JSON'
    ),
    url(
        r'^new_election_webform/$', display_and_process_html_for_new_webform_election,
        name="Show Page To Create Election via Webform"
    ),
    url(
        r'^new_election_via_nominee_links/$', display_and_process_html_for_new_nominee_links_election,
        name="Show Page To Create Election via Nominee Links"
    ),
    url(fr'^{ELECTION_SLUG_PATTERN}/$', get_nominees, name='Election Page'),
    url(
        fr'^{ELECTION_SLUG_PATTERN}/{ENDPOINT_MODIFY_VIA_JSON}/$',
        display_and_process_html_for_modification_of_json_election,
        name='Show Page to Update Election via JSON'
    ),
    url(
        fr'^{ELECTION_SLUG_PATTERN}/{ENDPOINT_MODIFY_VIA_WEBFORM}/$',
        display_and_process_html_for_modification_of_webform_election,
        name='Show Page to Update Election via Webform'
    ),
    url(
        fr'^{ELECTION_SLUG_PATTERN}/{ENDPOINT_MODIFY_VIA_NOMINEE_LINKS}/$',
        display_and_process_html_for_modification_of_election_and_nominee_links__nominee_links,
        name='Show Page for Updating an Election via Nominee Links'
    ),
    url(fr'^{ELECTION_SLUG_PATTERN}/delete/$', delete_selected_election, name="Delete Selected Election"),
    url(
        fr'^{ELECTION_SLUG_PATTERN}/{ENDPOINT_DELETE_NOMINEE_LINKS}/$',
        delete_selected_election__nominee_links,
        name="Delete Selected Election's Nominee Links"
    ),
    url(
        fr'^{ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK}/$',
        display_and_process_html_for_nominee_modification,
        name="Show Page for Election Officer to update a Nominee via Nominee Link"
    ),
    url(
        fr'^{ENDPOINT_CREATE_OR_UPDATE_NOMINEE_FOR_NOMINEE_VIA_PASSPHRASE__NOMINEE_LINK}/$',
        display_and_process_html_for_nominee_modification_via_passphrase,
        name="SHow Page for Nominees to update their own info"
    ),
    url(
        r'update_social_media_links/$', update_social_media_links, name='update_social_media_links'
    )
]
