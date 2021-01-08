import logging

from django.shortcuts import render

from about.models import OfficerEmailListAndPositionMapping
from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from about.views.position_mapping_helper import update_context, validate_position_index, validate_position_name
from csss.Constants import Constants
from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY, ERROR_MESSAGES_KEY, \
    there_are_multiple_entries
from querystring_parser import parser

logger = logging.getLogger('csss_site')

POSITION_NAME_KEY = 'position_name'
POSITION_EMAIL_KEY = 'position_email'

UNSAVED_POSITION_MAPPINGS_KEY = 'unsaved_position_mappings'


def input_new_officer_positions(request):
    logger.info(f"[about/position_mapping_helper.py officer_position_and_github_mapping()]"
                f" request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request,
                                                                                          TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = f'{error_message}<br>'
        return render_value
    context[ERROR_MESSAGES_KEY] = []
    if request.method == "POST":
        post_dict = parser.parse(request.POST.urlencode())
        if Constants.user_selected_to_add_new_officer_position in post_dict:
            success, context[ERROR_MESSAGES_KEY], context[UNSAVED_POSITION_MAPPINGS_KEY] = \
                add_new_position_mapping(post_dict)

    return render(request, 'about/position_mapping/position_mapping.html', update_context(context))


def add_new_position_mapping(post_dict):
    """
    Adds a new officer position mapping

    Keyword Argument
    post_dict -- request.POST in dictionary object

    Return
    success -- bool that is True or false
    error_message -- an error_message if the specified position index and position name are already used
    unsaved_position_mappings -- a dict that contains the unsaved position index
     and position names if one of them was invalid
    """
    error_messages = []
    if there_are_multiple_entries(post_dict, POSITION_NAME_KEY):
        logger.info(
            "[about/position_mapping_helper.py officer_position_and_github_mapping()] it appears "
            "that the user wants to create multiple new officers"
        )
        error_detected = False
        unsaved_position_mappings = []  # used to display all the submitted position if one of them had an
        # error which causes none of them to be saved

        # saves the position and position indexes checked so far so that the validator can check the
        # given position and its index against all in the database and the previous checked
        # positions and their indices
        submitted_position_names = []
        submitted_position_indices = []
        number_of_entries = len(post_dict[POSITION_NAME_KEY])
        for index in range(number_of_entries):
            position_name = post_dict[POSITION_NAME_KEY][index]
            position_index = post_dict[Constants.POSITION_INDEX_KEY][index]
            position_email = post_dict[POSITION_EMAIL_KEY][index]
            unsaved_position_mappings.append(
                {POSITION_NAME_KEY: position_name, Constants.POSITION_INDEX_KEY: position_index,
                 POSITION_EMAIL_KEY: position_email}
            )
            success, error_message = validate_position_mappings(position_index, position_name,
                                                                submitted_position_names=submitted_position_names,
                                                                submitted_position_indices=submitted_position_indices)
            submitted_position_names.append(position_name)
            submitted_position_indices.append(position_index)
            if not success:
                error_messages.append(f"{error_message}")
                logger.info(
                    "[about/position_mapping_helper.py officer_position_and_github_mapping()] "
                    f"unable to validate the new position {position_name} due to {error_message}"
                )
                error_detected = True
        if error_detected:
            return False, error_messages, unsaved_position_mappings
        else:
            logger.info(
                "[about/position_mapping_helper.py officer_position_and_github_mapping()] "
                "all new positions passed validation"
            )
            for index in range(number_of_entries):
                OfficerEmailListAndPositionMapping(position_name=post_dict[POSITION_NAME_KEY][index],
                                                   position_index=post_dict[Constants.POSITION_INDEX_KEY][index],
                                                   email=post_dict[POSITION_EMAIL_KEY][index]).save()
    else:
        success, error_message = \
            validate_position_mappings(post_dict[Constants.POSITION_INDEX_KEY], post_dict[POSITION_NAME_KEY])
        if success:
            logger.info(
                f"[about/position_mapping_helper.py officer_position_and_github_mapping()] "
                f"new position {post_dict[POSITION_NAME_KEY]} passed validation"
            )

            OfficerEmailListAndPositionMapping(position_name=post_dict[POSITION_NAME_KEY],
                                               position_index=post_dict[Constants.POSITION_INDEX_KEY],
                                               email=post_dict[POSITION_EMAIL_KEY]).save()
        else:
            logger.info(
                f"[about/position_mapping_helper.py officer_position_and_github_mapping()] unable to "
                f"save new position {post_dict[POSITION_NAME_KEY]} due to error {error_message}"
            )
            unsaved_position_mappings = [
                {POSITION_NAME_KEY: post_dict[POSITION_NAME_KEY], Constants.POSITION_INDEX_KEY: post_dict[Constants.POSITION_INDEX_KEY],
                 POSITION_EMAIL_KEY: post_dict[POSITION_EMAIL_KEY]}]
            error_messages.append(error_message)
            return False, error_messages, unsaved_position_mappings
    return True, error_messages, None


def validate_position_mappings(position_index, position_name, submitted_position_names=None,
                               submitted_position_indices=None):
    """
    Validates the new inputted position name and index

    Keyword Argument
    position_index -- the new position index
    position_name -- the new position name
    submitted_position_names -- other names specified by the user so far if they are
     submitting multiple positions at once
    submitted_position_indices -- other indexes specified by the user so far if they are submitting
     multiple positions at once

    Return
    success -- True or False if the new position name or index is not already used
    error_message -- an error_message if the name or index was already used
    """
    success, error_message = validate_position_index(position_index, submitted_position_indices)
    if not success:
        return success, error_message
    return validate_position_name(position_name, submitted_position_names)
