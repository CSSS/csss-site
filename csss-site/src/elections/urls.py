from django.conf.urls import url

from .views import election_management
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
]
