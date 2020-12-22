from django.conf.urls import url

from .views import officer_management, import_export_officer_lists, officer_creation_link_management
from .views.officer_position_mapping import position_mapping

urlpatterns = [

    url(r'^position_mapping$', position_mapping.position_mapping, name="Officer Position Mapping"),
    url(r'^list_of_officers$', officer_management.list_of_officers, name='CSSS List of Officers'),
    url(r'^who_we_are$', officer_management.who_we_are, name='Who We Are'),

    url(
        r'^show_create_link_page$',
        officer_creation_link_management.show_create_link_page,
        name='Show Page For Creating Links for Officer Information Input'),
    url(
        r'^show_page_with_creation_links$',
        officer_creation_link_management.show_page_with_creation_links,
        name="Create and display links that are used by officer to input their information"),
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
