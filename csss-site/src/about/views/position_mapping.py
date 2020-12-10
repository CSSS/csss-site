import logging

from django.shortcuts import render
from querystring_parser import parser

from about.models import OfficerEmailListAndPositionMapping, Term, Officer
from about.views.officer_management_helper import TAB_STRING
from csss.Constants import Constants
from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY, \
    there_are_multiple_entries, get_current_term, ERROR_MESSAGES_KEY

logger = logging.getLogger('csss_site')

OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID = "officer_email_list_and_position_mapping__id"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX = "officer_email_list_and_position_mapping__position_index"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_TYPE = "officer_email_list_and_position_mapping__position_name"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS = \
    "officer_email_list_and_position_mapping__email_list_address "


def display_position_mapping_html(request, context):
    position_mapping_for_selected_officer = OfficerEmailListAndPositionMapping.objects.all().order_by(
        'position_index')
    if len(position_mapping_for_selected_officer) > 0:
        context['position_mapping'] = position_mapping_for_selected_officer
    return render(request, 'about/position_mapping.html', context)


def position_mapping(request):
    """
    Handles any modifications done to position mappings
    """
    logger.info(f"[about/position_mapping.py position_mapping()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request,
                                                                                          TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = f'{error_message}<br>'
        return render_value
    context['OFFICER_POSITION_MAPPING__ID_KEY'] = OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID
    context['OFFICER_POSITION_MAPPING__POSITION_INDEX_KEY'] = OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX
    context['OFFICER_POSITION_MAPPING__POSITION_NAME_KEY'] = OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_TYPE
    context['OFFICER_POSITION_MAPPING__POSITION_EMAIL_KEY'] = \
        OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS

    if request.method != "POST":
        return display_position_mapping_html(request, context)
    post_dict = parser.parse(request.POST.urlencode())
    if Constants.user_select_to_a_position_mapping_option in post_dict:  # modifying an existing position mapping
        if post_dict[Constants.user_select_to_a_position_mapping_option] \
                == Constants.user_select_to_update_position_mapping:
            position_mapping_for_selected_officer = retrieve_officer_email_list_and_position_mapping_by_id(
                post_dict)
            if position_mapping_for_selected_officer is None:
                error_message = "id that was passed for position mapping was not correct"
                logger.info(f"[about/position_mapping.py position_mapping()] {error_message}")
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
                return display_position_mapping_html(request, context)

            logger.info("[about/position_mapping.py position_mapping()] the user's change to the position "
                        f"{position_mapping_for_selected_officer.position_name} was detected")
            # if anything has been changed for the selected position
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
            terms = Term.objects.all().filter(term_number=get_current_term())
            if len(terms) > 0:
                term = terms[0]
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
            position_mapping_for_selected_officer.position_name = new_name_for_officer_position
            position_mapping_for_selected_officer.position_index = \
                new_position_index_for_officer_position
            position_mapping_for_selected_officer.email = new_sfu_email_list_address_for_officer_position
            position_mapping_for_selected_officer.save()
            return display_position_mapping_html(request, context)

        elif post_dict[Constants.user_select_to_a_position_mapping_option] == \
                Constants.user_select_to_delete_position_mapping or \
                post_dict[Constants.user_select_to_a_position_mapping_option] \
                == Constants.user_select_to_un_delete_position_mapping:

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
    else:  # adding new position mapping[s]
        new_mapping_entries, error_message = get_new_position_mapping_entries(post_dict)
        if new_mapping_entries is None:
            context[ERROR_MESSAGES_KEY] = [error_message]
            return display_position_mapping_html(request, context)
        success, errors = validate_new_position_mapping_entries(new_mapping_entries)
        if not success:
            context[ERROR_MESSAGES_KEY] = errors
            context["unsaved_position_mappings"] = new_mapping_entries
            return display_position_mapping_html(request, context)
        save_new_positon_mappings(new_mapping_entries)
        return display_position_mapping_html(request, context)


def get_new_position_mapping_entries(post_dict):
    if Constants.position_name not in post_dict:
        logger.error(
            "[about/position_mapping.py get_new_position_mapping_entries()] could not find"
            f"any value for {Constants.position_name} in request.POST")
        return None, "Unable to find any of the names for the new positions"
    if Constants.position_index not in post_dict:
        logger.error(
            "[about/position_mapping.py get_new_position_mapping_entries()] could not find"
            f"any value for {Constants.position_index} in request.POST")
        return None, "Unable to find any of the indices for the new positions"
    if Constants.position_email not in post_dict:
        logger.error(
            "[about/position_mapping.py get_new_position_mapping_entries()] could not find"
            f"any value for {Constants.position_email} in request.POST")
        return None, "Unable to find any of the emails for the new positions"

    new_mapping_entries = []
    if there_are_multiple_entries(post_dict, Constants.position_name):
        for index in range(len(post_dict[Constants.position_name])):
            position_name = post_dict[Constants.position_name][index]
            position_index = post_dict[Constants.position_index][index]
            position_email = post_dict[Constants.position_email][index]
            new_mapping_entries.append({
                Constants.position_name: position_name,
                Constants.position_index: position_index,
                Constants.position_email: position_email
            }
            )
    else:
        new_mapping_entries.append(
            {Constants.position_name: post_dict[Constants.position_name],
             Constants.position_index: post_dict[Constants.position_index],
             Constants.position_email: post_dict[Constants.position_email]}
        )
    return new_mapping_entries, None


def validate_new_position_mapping_entries(new_mapping_entries):
    submitted_positions = []
    submitted_position_indexes = []
    overall_success = True
    error_messages = []
    for new_mapping in new_mapping_entries:
        logger.info(f"[about/position_mapping.py validate_new_position_mapping_entries()] validating "
                    f"new position index {new_mapping[Constants.position_index]}"
                    f" with name {new_mapping[Constants.position_name]}")
        success, error_message = validate_position_mappings(
            new_mapping[Constants.position_index],
            new_mapping[Constants.position_name],
            submitted_positions=submitted_positions, submitted_position_indexes=submitted_position_indexes
        )
        submitted_positions.append(new_mapping[Constants.position_name])
        submitted_position_indexes.append(new_mapping[Constants.position_index])
        if not success:
            overall_success = False
            error_messages.append(f"{error_message}")
            logger.info("[about/position_mapping.py validate_new_position_mapping_entries()] "
                        "unable to validate the new position"
                        f" {new_mapping[Constants.position_name]} due to {error_message}")
    return overall_success, error_messages


def save_new_positon_mappings(new_mapping_entries):
    for new_mapping in new_mapping_entries:
        position_name = new_mapping[Constants.position_name]
        position_index = new_mapping[Constants.position_index]
        position_email = new_mapping[Constants.position_email]
        OfficerEmailListAndPositionMapping(position_name=position_name,
                                           position_index=position_index,
                                           email=position_email).save()


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
        return None
    if not f"{post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID]}".isdigit():
        logger.error(
            "[about/position_mapping.py retrieve_officer_email_list_and_position_mapping_by_id()] the id"
            f" of {post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID]} is not a valid digit in request.POST")
        return None
    position_mapping_id = int(post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID])
    if len(OfficerEmailListAndPositionMapping.objects.all().filter(id=position_mapping_id)) == 0:
        logger.error(
            "[about/position_mapping.py retrieve_officer_email_list_and_position_mapping_by_id()] could not find any "
            f"position mappings that correspond to id {position_mapping_id}")
        return None
    return OfficerEmailListAndPositionMapping.objects.get(id=position_mapping_id)


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
        return None, None, None, "could not find a new valid position index in input"
    if OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_TYPE not in post_dict:
        logger.error(
            "[about/position_mapping.py retrieve_new_position_info_for_officer_position()] could not find"
            f"any value for {OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_TYPE} in request.POST")
        return None, None, None, "could not find the new position name in input"
    if OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS not in post_dict:
        logger.error(
            "[about/position_mapping.py retrieve_new_position_info_for_officer_position()] could not find"
            f"any value for {OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS} in request.POST")
        return None, None, None, "could not find the new position email address in input"

    new_position_index = int(new_position_index)
    new_position_name = post_dict[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_TYPE]
    new_sfu_email_list_address_for_officer_position = post_dict[
        OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS]
    return new_position_index, new_position_name, new_sfu_email_list_address_for_officer_position, None


def validate_position_index(position_index, submitted_position_indexes=None):
    """
    Validates the new inputted position index

    Keyword Argument
    position_index -- the new position index
    submitted_position_indexes -- other indexes specified by the user so far
     if they are submitting multiple positions at once

    Return
    success -- True or False if the new position index is not already used
    error_message -- an error_message if the index was already used
    """
    if submitted_position_indexes is None:
        submitted_position_indexes = []
    if len(OfficerEmailListAndPositionMapping.objects.all().filter(
            position_index=position_index)) > 0 or position_index in submitted_position_indexes:
        logger.info(f"[about/position_mapping.py validate_position_index()] validate for position index "
                    f"{position_index} was unsuccessful")
        return False, f"Another Position already has an index of {position_index}"
    logger.info(f"[about/position_mapping.py validate_position_index()] validate for position index "
                f"{position_index} was successful")
    return True, None


def validate_position_name(position_name, submitted_position_names=None):
    """
    Validates the new inputted position name

    Keyword Argument
    position_name -- the new position name
    submitted_position_names -- other names specified by the user so far if they
     are submitting multiple positions at once

    Return
    success -- True or False if the new position name is not already used
    error_message -- an error_message if the name was already used
    """
    if submitted_position_names is None:
        submitted_position_names = []
    if len(OfficerEmailListAndPositionMapping.objects.all().filter(
            position_name=position_name)) > 0 or position_name in submitted_position_names:
        logger.info(f"[about/position_mapping.py validate_position_name()] validate for position name "
                    f"{position_name} was unsuccessful")
        return False, f"the position of {position_name} already exists"
    logger.info(f"[about/position_mapping.py validate_position_name()] validate for position name "
                f"{position_name} was successful")
    return True, None


def validate_position_mappings(position_index, position_name, submitted_positions=None,
                               submitted_position_indexes=None):
    """
    Validates the new inputted position name and index

    Keyword Argument
    position_name -- the new position name
    position_index -- the new position index
    submitted_position_names -- other names specified by the user so far if they are
     submitting multiple positions at once
    submitted_position_indexes -- other indexes specified by the user so far if they are submitting
     multiple positions at once

    Return
    success -- True or False if the new position name or index is not already used
    error_message -- an error_message if the name or index was already used
    """
    success, error_message = validate_position_index(position_index, submitted_position_indexes)
    if not success:
        return success, error_message
    success, error_message = validate_position_name(position_name, submitted_positions)
    if not success:
        return success, error_message
    return True, None
