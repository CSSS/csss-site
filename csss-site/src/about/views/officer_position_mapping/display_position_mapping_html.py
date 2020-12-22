from django.shortcuts import render

from about.models import OfficerEmailListAndPositionMapping

OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID = "officer_email_list_and_position_mapping__id"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX = "officer_email_list_and_position_mapping__position_index"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME = "officer_email_list_and_position_mapping__position_name"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS = \
    "officer_email_list_and_position_mapping__email_list_address "


def display_position_mapping_html(request, context):
    context['OFFICER_POSITION_MAPPING__ID_KEY'] = OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID
    context['OFFICER_POSITION_MAPPING__POSITION_INDEX_KEY'] = OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX
    context['OFFICER_POSITION_MAPPING__POSITION_NAME_KEY'] = OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME
    context['OFFICER_POSITION_MAPPING__POSITION_EMAIL_KEY'] = \
        OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS
    position_mapping_for_selected_officer = OfficerEmailListAndPositionMapping.objects.all().order_by(
        'position_index')
    if len(position_mapping_for_selected_officer) > 0:
        context['position_mapping'] = position_mapping_for_selected_officer
    return render(request, 'about/position_mapping.html', context)
