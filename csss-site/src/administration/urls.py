from django.conf.urls import url
from . import views, election_management, officer_management


urlpatterns = [
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^elections/create$', election_management.create_specified_election, name='create_election'),
    url(
        r'^elections/create_or_update_json$',
        election_management.create_or_update_specified_election_with_provided_json,
        name='update_election_json'
    ),
    url(r'^elections/select_election$', election_management.select_election_to_update, name='select_election'),
    url(
        r'^elections/determine_election_action$',
        election_management.determine_election_action,
        name='determine_election_action'
    ),
    url(r'^elections/update$', election_management.update_specified_election, name='update_election'),
    url(r'^officer/show_create_link_page$', officer_management.show_create_link_page, name='Create Link'),
    url(r'^officer/create_link$', officer_management.create_link, name='Create Link'),
    url(
        r'^officer/create_or_update_json$',
        officer_management.create_or_update_specified_term_with_provided_json,
        name='Create Link'
    )
]
