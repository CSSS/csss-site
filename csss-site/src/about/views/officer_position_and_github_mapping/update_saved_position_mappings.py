import logging

from django.shortcuts import render
from querystring_parser import parser

from about.models import OfficerEmailListAndPositionMapping, Term, Officer
from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from about.views.position_mapping_helper import update_context, validate_position_index, validate_position_name, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID, OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS
from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY, ERROR_MESSAGES_KEY, \
    get_current_term

DELETE_POSITION_MAPPING_KEY = 'delete_position_mapping'
UN_DELETED_POSITION_MAPPING_KEY = 'un_delete_position_mapping'
UPDATE_POSITION_MAPPING_KEY = 'update_position_mapping'

logger = logging.getLogger('csss_site')


def update_saved_position_mappings(request):
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request,
                                                                                          TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = f'{error_message}<br>'
        return render_value

    if request.method == "POST":
        post_dict = parser.parse(request.POST.urlencode())
        if DELETE_POSITION_MAPPING_KEY in post_dict or UN_DELETED_POSITION_MAPPING_KEY in post_dict:
            success, error_message = _delete_or_undelete_position_mapping(post_dict)
            if not success:
                context[ERROR_MESSAGES_KEY] = [f"{error_message}"]
        elif UPDATE_POSITION_MAPPING_KEY in post_dict:
            context[ERROR_MESSAGES_KEY] = _update_position_mapping(post_dict)
    return render(request, 'about/position_mapping/position_mapping.html', update_context(context))


def _delete_or_undelete_position_mapping(post_dict):
    """
    Toggles a Position Mapping's delete attribute

    Keyword Argument
    post_dict -- request.POST in dictionary object

    Return
    success -- bool that is True or false
    error_message -- an error_message if no valid position mapping ID is found, None otherwise

    """
    if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID in post_dict
            and f"{post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID]}".isdigit()
            and len(
                OfficerEmailListAndPositionMapping.objects.all().filter(
                    id=int(post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID])
                )
            ) > 0):
        return False, "No valid ID for a position mapping found"

    position_mapping_for_selected_officer = OfficerEmailListAndPositionMapping.objects.get(
        id=int(post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID])
    )
    position_mapping_for_selected_officer.marked_for_deletion = DELETE_POSITION_MAPPING_KEY in post_dict
    position_mapping_for_selected_officer.save()
    logger.info(
        f"[about/update_saved_position_mappings.py _delete_or_undelete_position_mapping()] deletion for position"
        f" {position_mapping_for_selected_officer.position_name} set to"
        f" {position_mapping_for_selected_officer.marked_for_deletion}"
    )
    return True, None


def _update_position_mapping(post_dict):
    """
    Updates the position mapping for the specified position

    Keyword Argument
    post_dict -- request.POST in dictionary object

    Return
    error_messages -- a list of all the possible error messages
    """
    if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID in post_dict
            and f"{post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID]}".isdigit()
            and len(
                OfficerEmailListAndPositionMapping.objects.all().filter(
                    id=int(post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID])
                )
            ) > 0):
        error_message = "No valid position mapping id detected"
        logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
        return [error_message]

    if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX in post_dict
            and f"{post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX]}".isdigit()):
        error_message = "No valid position index detected for position mapping"
        logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
        return [error_message]
    if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME in post_dict):
        error_message = "No valid position name detected for position mapping"
        logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
        return [error_message]
    if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS in post_dict):
        error_message = "No valid position email list detected for position mapping"
        logger.info(f"[about/update_saved_position_mappings.py _update_position_mapping()] {error_message}")
        return [error_message]

    position_mapping_for_selected_officer = OfficerEmailListAndPositionMapping.objects.get(
        id=int(post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID])
    )
    logger.info(
        f"[about/update_saved_position_mappings.py _update_position_mapping()] "
        f"user has selected to update the position {position_mapping_for_selected_officer.position_name}"
    )

    new_position_index_for_officer_position = int(post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX])
    new_name_for_officer_position = post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME]
    new_sfu_email_list_address_for_officer_position = \
        post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS]

    if new_name_for_officer_position == position_mapping_for_selected_officer.position_name \
            and new_position_index_for_officer_position == position_mapping_for_selected_officer.position_index \
            and new_sfu_email_list_address_for_officer_position == position_mapping_for_selected_officer.email:
        return []

    logger.info(
        f"[about/update_saved_position_mappings.py _update_position_mapping()] the user's "
        f"change to the position {position_mapping_for_selected_officer.position_name} was detected"
    )
    # if anything has been changed for the selected position
    success = True
    error_message = None
    previous_position_index = position_mapping_for_selected_officer.position_index
    previous_position_name = position_mapping_for_selected_officer.position_name
    if new_position_index_for_officer_position != previous_position_index:
        success, error_message = validate_position_index(new_position_index_for_officer_position)
    if success and new_name_for_officer_position != previous_position_name:
        success, error_message = validate_position_name(new_name_for_officer_position)

    if success:
        terms = Term.objects.all().filter(term_number=get_current_term())
        if len(terms) > 0:
            term = terms[0]
            officers_in_current_term_that_need_update = Officer.objects.all().filter(
                elected_term=term,
                position_index=position_mapping_for_selected_officer.position_index
            )
            logger.info(
                f"[about/update_saved_position_mappings.py _update_position_mapping()] updating"
                f" {len(officers_in_current_term_that_need_update)} officers due to change in position"
                f" {position_mapping_for_selected_officer.position_name}"
            )
            for officer_in_current_term_that_need_update in officers_in_current_term_that_need_update:
                officer_in_current_term_that_need_update.position_index = new_position_index_for_officer_position
                officer_in_current_term_that_need_update.sfu_officer_mailing_list_email = \
                    new_sfu_email_list_address_for_officer_position
                officer_in_current_term_that_need_update.position_name = new_name_for_officer_position
                officer_in_current_term_that_need_update.save()
        position_mapping_for_selected_officer.position_name = new_name_for_officer_position
        position_mapping_for_selected_officer.position_index = new_position_index_for_officer_position
        position_mapping_for_selected_officer.email = new_sfu_email_list_address_for_officer_position
        position_mapping_for_selected_officer.save()
    else:
        logger.info(
            "[about/update_saved_position_mappings.py _update_position_mapping()]"
            f" encountered error {error_message} when trying to update position"
            f" {position_mapping_for_selected_officer.position_name}"
        )

    return [error_message]
