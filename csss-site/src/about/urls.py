from django.conf.urls import url

from .views import officer_management, import_export_officer_lists
from .views.generate_officer_creation_links import officer_creation_link_management
from .views.github_position_mapping.github_mapping import github_mapping
from .views.github_position_mapping.save_new_github_officer_team_mapping import save_new_github_officer_team_mapping
from .views.github_position_mapping.update_saved_github_mappings import update_saved_github_mappings
from .views.input_new_officers.specify_new_officers.delete_new_officers import delete_new_officers
from .views.input_new_officers.specify_new_officers.specify_new_officers import specify_new_officers
from .views.officer_positions.input_new_officer_positions import input_new_officer_positions
from .views.officer_positions.officer_positions import officer_positions
from .views.officer_positions.update_saved_position_mappings import update_saved_position_mappings

urlpatterns = [
    url(
        r'^specify_new_officers$',
        specify_new_officers,
        name='Specify Positions for New Officers'
    ),
    url(
        r'^specify_new_officers/delete$',
        delete_new_officers,
        name='Specify Positions for New Officers'
    ),
    url(
        r'^officer_position$', officer_positions,
        name="Officer Position Mapping"
    ),
    url(
        r'^officer_position/update_saved_position_mappings$',
        update_saved_position_mappings,
        name="Officer Position Mapping"
    ),
    url(
        r'^officer_position/input_new_officer_positions$',
        input_new_officer_positions,
        name="Officer Position Mapping"
    ),
    url(
        r'^github_mapping$', github_mapping,
        name="Officer Position Mapping"
    ),
    url(
        r'^github_mapping/update_saved_github_mappings$',
        update_saved_github_mappings,
        name="Officer Position Mapping"
    ),
    url(
        r'^github_mapping/save_new_github_officer_team_mapping$',
        save_new_github_officer_team_mapping,
        name="Officer Position Mapping"
    ),
    url(
        r'^list_of_current_officers$',
        officer_management.list_of_current_officers,
        name='CSSS List of Current Officers'
    ),
    url(r'^list_of_past_officers$', officer_management.list_of_past_officers, name='CSSS List of Past Officers'),
    url(r'^who_we_are$', officer_management.who_we_are, name='Who We Are'),
    url(
        r'^allow_officer_to_choose_name$',
        officer_creation_link_management.allow_officer_to_choose_name,
        name='Add an Officer'),
    url(
        r'^display_page_for_officer_to_input_info$',
        officer_creation_link_management.display_page_for_officers_to_input_their_info,
        name='Add an Officer'),
    url(
        r'^input_officer_info$',
        officer_creation_link_management.process_information_entered_by_officer,
        name='Add an Officer'),

    url(
        r'^show_page_for_inputting_officer_info$',
        import_export_officer_lists.show_page_for_uploading_officer_list,
        name="Show Page for Taking in Officer List"),
    url(
        r'^upload_officer_list$',
        import_export_officer_lists.process_officer_list_upload,
        name="Process Uploaded Officer List"
    ),
]
