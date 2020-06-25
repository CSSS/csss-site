from django.conf.urls import url

from .views import election_views, gdrive_views, github_views, login_views, officer_views, resource_views

urlpatterns = [
    url(r'^login$', login_views.login, name='login'),
    url(r'^logout$', login_views.logout, name='logout'),
    url(r'^elections/create$', election_views.create_specified_election, name='create_election'),
    url(
        r'^elections/create_or_update_json$',
        election_views.create_or_update_specified_election_with_provided_json,
        name='update_election_json'
    ),
    url(r'^elections/select_election$', election_views.select_election_to_update, name='select_election'),
    url(
        r'^elections/determine_election_action$',
        election_views.determine_election_action,
        name='determine_election_action'
    ),
    url(r'^elections/update$', election_views.update_specified_election, name='update_election'),

    url(r'^officer/show_create_link_page$', officer_views.show_create_link_page, name='Create Link'),
    url(r'^officer/create_link$', officer_views.show_page_with_creation_links, name='Create Link'),
    url(r'^officer/process_exec_info$', officer_views.process_information_entered_by_officer, name='Add an Exec'),
    url(
        r'^resources/select_resources$',
        resource_views.select_resource_to_manage,
        name="Select Resource"
    ),
    url(
        r'^resources/selected_resource$',
        resource_views.manage_selected_resource,
        name="Selected Resource"
    ),
    url(r'^resources/gdrive/$',
        gdrive_views.gdrive_index,
        name="Google Drive Management"
        ),
    url(
        r'^resources/gdrive/add_users_gdrive$',
        gdrive_views.add_users_to_gdrive,
        name="Grant Users Google Drive Access"
    ),
    url(
        r'^resources/gdrive/update_current_gdrive_user$',
        gdrive_views.update_permissions_for_existing_gdrive_user,
        name="Update Current GDrive Users"
    ),
    url(
        r'^resources/gdrive/make_folder_public_gdrive',
        gdrive_views.make_folders_public_gdrive,
        name="Grant Users Google Drive Access"
    ),
    url(
        r'^resources/gdrive/update_gdrive_public_linls',
        gdrive_views.update_gdrive_public_links,
        name="Update Current GDrive Users"
    ), url(
        r'^resources/github$',
        github_views.index,
        name="Github Management"
    ),
    url(
        r'^resources/github/add_non_officer_to_github_team',
        github_views.add_non_officer_to_github_team,
        name="Add Non Officer To Github Teams"
    ), url(
        r'^resources/github/update_github_non_officer',
        github_views.update_github_non_officer,
        name="Update Non Officer"
    ),
    url(
        r'^resources/validate_access$',
        resource_views.validate_access,
        name="Validate CSSS Digital resources"
    )
]
