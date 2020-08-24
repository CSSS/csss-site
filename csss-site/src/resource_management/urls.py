from django.conf.urls import url

from resource_management.views import github_views, gdrive_views, resource_views

urlpatterns = [
    url(
        r'^show_resources_for_validation$',
        resource_views.show_resources_to_validate,
        name="Select Resource"
    ),
    url(
        r'^validate_access$',
        resource_views.validate_access,
        name="Validate CSSS Digital resources"
    ),
    url(r'^gdrive/$',
        gdrive_views.gdrive_index,
        name="Google Drive Management"
        ),
    url(
        r'^gdrive/add_users_gdrive$',
        gdrive_views.add_users_to_gdrive,
        name="Grant Users Google Drive Access"
    ),
    url(
        r'^gdrive/update_current_gdrive_user$',
        gdrive_views.update_permissions_for_existing_gdrive_user,
        name="Update Current GDrive Users"
    ),
    url(
        r'^gdrive/make_folder_public_gdrive',
        gdrive_views.make_folders_public_gdrive,
        name="Grant Users Google Drive Access"
    ),
    url(
        r'^gdrive/update_gdrive_public_linls',
        gdrive_views.update_gdrive_public_links,
        name="Update Current GDrive Users"
    ), url(
        r'^github$',
        github_views.index,
        name="Github Management"
    ),
    url(
        r'^github/add_non_officer_to_github_team',
        github_views.add_non_officer_to_github_team,
        name="Add Non Officer To Github Teams"
    ), url(
        r'^github/update_github_non_officer',
        github_views.update_github_non_officer,
        name="Update Non Officer"
    )
]
