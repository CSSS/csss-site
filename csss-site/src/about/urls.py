from django.conf.urls import url

from .views.input_new_officers.specify_new_officers.specify_new_officers import specify_new_officers
from .views.input_new_officers.enter_new_officer_info.enter_new_officer_info import enter_new_officer_info
from .views.Constants import ENTER_NEW_OFFICER_INFO_URL
from .views.input_new_officers.delete_new_officers.delete_new_officers import delete_new_officers
from .views.officer_positions.officer_positions import officer_positions
from .views.officer_positions.update_saved_position_mappings import update_saved_position_mappings
from .views.officer_positions.input_new_officer_positions import input_new_officer_positions
from .views.github_position_mapping.github_mapping import github_mapping
from .views.github_position_mapping.update_saved_github_mappings import update_saved_github_mappings
from .views.github_position_mapping.save_new_github_officer_team_mapping import save_new_github_officer_team_mapping

from .views import officer_management, import_export_officer_lists

urlpatterns = [
    url(r'^specify_new_officers$', specify_new_officers, name='Specify Positions for New Officers'),
    url(fr'^{ENTER_NEW_OFFICER_INFO_URL}$', enter_new_officer_info, name='Allow officer to enter their info'),
    url(r'^specify_new_officers/delete$', delete_new_officers, name='Specify Positions for New Officers'),
    url(r'^officer_position$', officer_positions, name="Officer Position Mapping"),
    url(
        r'^officer_position/update_saved_position_mappings$',
        update_saved_position_mappings,
        name="Officer Position Mapping"
    ),
    url(r'^officer_position/input_new_officer_positions$', input_new_officer_positions,
        name="Officer Position Mapping"),
    url(r'^github_mapping$', github_mapping, name="Officer Position Mapping"),
    url(r'^github_mapping/update_saved_github_mappings$', update_saved_github_mappings,
        name="Officer Position Mapping"),
    url(
        r'^github_mapping/save_new_github_officer_team_mapping$',
        save_new_github_officer_team_mapping,
        name="Officer Position Mapping"
    ),
    url(r'^list_of_current_officers$', officer_management.list_of_current_officers,
        name='CSSS List of Current Officers'),
    url(r'^list_of_past_officers$', officer_management.list_of_past_officers, name='CSSS List of Past Officers'),
    url(r'^who_we_are$', officer_management.who_we_are, name='Who We Are'),
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
