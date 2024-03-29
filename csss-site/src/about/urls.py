from django.conf.urls import url

from .views import import_export_officer_lists
from .views.Constants import ENTER_NEW_OFFICER_INFO_URL, CURRENT_EMAIL_MAPPINGS_URL
from .views.github_position_mapping.github_mapping import github_mapping
from .views.github_position_mapping.save_new_github_officer_team_mapping import save_new_github_officer_team_mapping
from .views.github_position_mapping.update_saved_github_mappings import update_saved_github_mappings
from .views.input_new_officers.delete_new_officers.delete_new_officers import delete_new_officers
from .views.input_new_officers.enter_new_officer_info.enter_new_officer_info import enter_new_officer_info
from .views.input_new_officers.specify_new_officers.specify_new_officers import specify_new_officers
from .views.list_of_officers.list_of_current_officers import list_of_current_officers
from .views.list_of_officers.list_of_past_officers import list_of_past_officers
from .views.officer_positions.current_email_mapping import current_email_mapping
from .views.officer_positions.input_new_officer_positions import input_new_officer_positions
from .views.officer_positions.officer_positions import officer_positions
from .views.officer_positions.update_saved_position_mappings import update_saved_position_mappings
from .views.who_we_are import who_we_are

urlpatterns = [
    url(r'^specify_new_officers$', specify_new_officers, name='Specify Positions for New Officers'),
    url(r'^specify_new_officers/delete$', delete_new_officers, name='Specify Positions for New Officers'),
    url(fr'^{ENTER_NEW_OFFICER_INFO_URL}$', enter_new_officer_info, name='Allow officer to enter their info'),
    url(fr'^{CURRENT_EMAIL_MAPPINGS_URL}$', current_email_mapping, name="Get the current mapping workflow"),
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
        list_of_current_officers,
        name='CSSS List of Current Officers'
    ),
    url(r'^list_of_past_officers$', list_of_past_officers, name='CSSS List of Past Officers'),
    url(r'^who_we_are$', who_we_are, name='Who We Are'),


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
