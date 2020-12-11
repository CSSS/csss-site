import logging

from about.models import Officer, OfficerEmailListAndPositionMapping
from about.views.officer_position_mapping.position_mapping import display_position_mapping_html, \
    validate_position_index, validate_position_name, OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX, OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS
from csss.Constants import Constants
from csss.views_helper import ERROR_MESSAGES_KEY, get_current_term_obj

logger = logging.getLogger('csss_site')


def modify_existing_position_mapping(request, context, post_dict):
    if post_dict[Constants.user_select_to_a_position_mapping_option] \
            == Constants.user_select_to_update_position_mapping:
        return update_existing_position_mapping(request, context, post_dict)
    elif post_dict[Constants.user_select_to_a_position_mapping_option] == \
            Constants.user_select_to_delete_position_mapping or \
            post_dict[Constants.user_select_to_a_position_mapping_option] \
            == Constants.user_select_to_un_delete_position_mapping:
        return update_deletion_status_for_position_mapping(request, context, post_dict)


def update_existing_position_mapping(request, context, post_dict):
    """
    updates an existing position mapping

    Keyword Argument
    request -- the django request object
    context -- the context dictionary
    post_dict -- a dictionary representation of request.POST

    Return
    the HttpResponse
    """
    position_mapping_for_selected_officer, error_message = retrieve_officer_email_list_and_position_mapping_by_id(
        post_dict)
    if position_mapping_for_selected_officer is None:
        context[ERROR_MESSAGES_KEY] = [error_message]
        return display_position_mapping_html(request, context)

    new_position_index_for_officer_position, new_name_for_officer_position, \
    new_sfu_email_list_address_for_officer_position, error_message \
        = retrieve_new_position_info_for_officer_position(post_dict)

    if new_position_index_for_officer_position is None or new_name_for_officer_position is None \
            or new_sfu_email_list_address_for_officer_position is None:
        context[ERROR_MESSAGES_KEY] = [error_message]
        return display_position_mapping_html(request, context)

    logger.info("[about/position_mapping.py position_mapping()] user has selected to update the "
                f"position {position_mapping_for_selected_officer.position_name} ")

    if (new_name_for_officer_position == position_mapping_for_selected_officer.position_name and
            new_position_index_for_officer_position ==
            position_mapping_for_selected_officer.position_index and
            new_sfu_email_list_address_for_officer_position ==
            position_mapping_for_selected_officer.email):
        context[ERROR_MESSAGES_KEY] = ["No changes detected to select position mapping"]
        return display_position_mapping_html(request, context)

    logger.info("[about/position_mapping.py position_mapping()] the user's change to the position "
                f"{position_mapping_for_selected_officer.position_name} was detected")
    success = True
    previous_position_index = position_mapping_for_selected_officer.position_index
    previous_position_name = position_mapping_for_selected_officer.position_name
    if new_position_index_for_officer_position != previous_position_index:
        success, error_message = validate_position_index(new_position_index_for_officer_position)
    if success and new_name_for_officer_position != previous_position_name:
        success, error_message = validate_position_name(new_name_for_officer_position)

    if not success:
        logger.info("[about/position_mapping.py position_mapping()] encountered error "
                    f"{error_message} when trying to update "
                    f"position {position_mapping_for_selected_officer.position_name}")
        context[ERROR_MESSAGES_KEY] = [error_message]
        return display_position_mapping_html(request, context)

    update_officer_in_current_term_to_reflect_change_in_corresponding_position_mapping(
        position_mapping_for_selected_officer, new_position_index_for_officer_position,
        new_sfu_email_list_address_for_officer_position, new_name_for_officer_position
    )
    update_corresponding_position_mapping(
        position_mapping_for_selected_officer, new_name_for_officer_position,
        new_position_index_for_officer_position, new_sfu_email_list_address_for_officer_position
    )

    return display_position_mapping_html(request, context)


def retrieve_officer_email_list_and_position_mapping_by_id(post_dict):
    """
    Get a position mapping by id

    Keyword Argument
    post_dict - dict version of the request.POST

    Return
    OfficerEmailListAndPositionMapping -- the object that corresponds to the id or None
    """
    if OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID not in post_dict:
        logger.error(
            "[about/position_mapping.py retrieve_officer_email_list_and_position_mapping_by_id()] could not find"
            f"any value for {OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID} in request.POST")
        return None, "could not find an id for the modified position mapping"
    if not f"{post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID]}".isdigit():
        logger.error(
            "[about/position_mapping.py retrieve_officer_email_list_and_position_mapping_by_id()] the id"
            f" of {post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID]} is not a valid digit in request.POST")
        return None, "id that was passed for position mapping was not correct"
    position_mapping_id = int(post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID])
    if len(OfficerEmailListAndPositionMapping.objects.all().filter(id=position_mapping_id)) == 0:
        logger.error(
            "[about/position_mapping.py retrieve_officer_email_list_and_position_mapping_by_id()] could not find any "
            f"position mappings that correspond to id {position_mapping_id}")
        return None, "id that was passed for position mapping does not map to an existing position mapping"
    return OfficerEmailListAndPositionMapping.objects.get(id=position_mapping_id), None


def retrieve_new_position_info_for_officer_position(post_dict):
    """
    Retrieves the new info for the officer position

    Keyword Argument
    post_dict - dict version of the request.POST

    Return
    new_position_index -- the new position_index specified by the user
    new_position_name -- the new position_name specified by the user
    new_sfu_email_list_address_for_officer_position -- the new position_sfu_email_list_address specified by the user
    error_message -- error message, if there is one
    """
    if OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX not in post_dict:
        logger.error(
            "[about/position_mapping.py retrieve_new_position_info_for_officer_position()] could not find"
            f"any value for {OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX} in request.POST")
        return None, None, None, "could not find the new position index in input"
    new_position_index = post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX]
    if not f"{new_position_index}".isdigit():
        logger.error(
            "[about/position_mapping.py retrieve_new_position_info_for_officer_position()] the id"
            f" of {post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX]} "
            f"is not a valid digit in request.POST")
        return None, None, None, "the inputted position index does not appear to be a number"
    if OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME not in post_dict:
        logger.error(
            "[about/position_mapping.py retrieve_new_position_info_for_officer_position()] could not find"
            f"any value for {OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME} in request.POST")
        return None, None, None, "could not find the new position name in input"
    if OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS not in post_dict:
        logger.error(
            "[about/position_mapping.py retrieve_new_position_info_for_officer_position()] could not find"
            f"any value for {OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS} in request.POST")
        return None, None, None, "could not find the new position email address in input"

    new_position_index = int(new_position_index)
    new_position_name = post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME]
    new_sfu_email_list_address_for_officer_position = post_dict[
        OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS]
    return new_position_index, new_position_name, new_sfu_email_list_address_for_officer_position, None


def update_officer_in_current_term_to_reflect_change_in_corresponding_position_mapping(
        position_mapping_for_selected_officer, new_position_index_for_officer_position,
        new_sfu_email_list_address_for_officer_position, new_name_for_officer_position
):
    """
    Updates all the officers in the current term whose corresponding position mapping was updated

    Keyword Argument
    position_mapping_for_selected_officer -- the position mapping that will be updated
    new_position_index_for_officer_position -- the new position index to be assigned to any officers
    new_sfu_email_list_address_for_officer_position --  the new sfu email list address to be assigned to any officers
    new_name_for_officer_position --  the new position name to be assigned to any officers
    """
    term = get_current_term_obj()
    if term is None:
        return
    officer_in_current_term_that_need_update = Officer.objects.all().filter(
        elected_term=term,
        position_name=position_mapping_for_selected_officer.position_name
    )
    logger.info("[about/position_mapping.py position_mapping()] updating "
                f"{len(officer_in_current_term_that_need_update)} officers "
                f"due to change in position "
                f"{position_mapping_for_selected_officer.position_name}")
    for officer in officer_in_current_term_that_need_update:
        officer.position_index = new_position_index_for_officer_position
        officer.sfu_officer_mailing_list_email = \
            new_sfu_email_list_address_for_officer_position
        officer.position_name = new_name_for_officer_position
        officer.save()


def update_corresponding_position_mapping(
        position_mapping_for_selected_officer, new_name_for_officer_position,
        new_position_index_for_officer_position, new_sfu_email_list_address_for_officer_position):
    """
    Updates the specified position mapping with the given name, index and sfu email list address

    Keyword Argument
    position_mapping_for_selected_officer -- the position mapping to update
    new_name_for_officer_position -- the new name to be assigned to given position mapping
    new_position_index_for_officer_position --  the new index to be assigned to the given position mapping
    new_sfu_email_list_address_for_officer_position -- the new sfu email list address to be assigned to the given position mapping
    """
    position_mapping_for_selected_officer.position_name = new_name_for_officer_position
    position_mapping_for_selected_officer.position_index = \
        new_position_index_for_officer_position
    position_mapping_for_selected_officer.email = new_sfu_email_list_address_for_officer_position
    position_mapping_for_selected_officer.save()


def update_deletion_status_for_position_mapping(request, context, post_dict):
    """
    Update whether or not a position mapping needs to be deleted

    Keyword Argument
    request -- the django request object
    context -- the context dictionary
    post_dict -- a dictionary representation of request.POST

    Return
    the HttpResponse
    """
    position_mapping_for_selected_officer = retrieve_officer_email_list_and_position_mapping_by_id(
        post_dict)
    if position_mapping_for_selected_officer is None:
        error_message = "id that was passed for position mapping was not correct"
        logger.info(f"[about/position_mapping.py position_mapping()] {error_message}")
        context[ERROR_MESSAGES_KEY] = [error_message]
        return display_position_mapping_html(request, context)
    position_mapping_for_selected_officer.marked_for_deletion = \
        post_dict[Constants.user_select_to_a_position_mapping_option] == \
        Constants.user_select_to_delete_position_mapping
    logger.info("[about/position_mapping.py position_mapping()] deletion for position "
                f"{position_mapping_for_selected_officer.position_name} set to  "
                f"{position_mapping_for_selected_officer.marked_for_deletion}")
    position_mapping_for_selected_officer.save()
    return display_position_mapping_html(request, context)
