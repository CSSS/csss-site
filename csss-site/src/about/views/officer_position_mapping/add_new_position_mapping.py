import logging

from about.models import OfficerEmailListAndPositionMapping
from about.views.officer_position_mapping.display_position_mapping_html import display_position_mapping_html
from about.views.officer_position_mapping.position_attribute_validation import validate_position_index, \
    validate_position_name
from csss.Constants import Constants
from csss.views_helper import ERROR_MESSAGES_KEY, there_are_multiple_entries

logger = logging.getLogger('csss_site')


def add_new_position_mapping(request, context, post_dict):
    """
    Adds new position mappings

    Keyword Argument
    request -- the django request object
    context -- the context dictionary
    post_dict -- a dictionary representation of request.POST

    Return
    the HttpResponse
    """
    new_mapping_entries, error_message = get_new_position_mapping_entries(post_dict)
    if new_mapping_entries is None:
        context[ERROR_MESSAGES_KEY] = [error_message]
        return display_position_mapping_html(request, context)
    success, errors = validate_new_position_mapping_entries(new_mapping_entries)
    if not success:
        context[ERROR_MESSAGES_KEY] = errors
        context["unsaved_position_mappings"] = new_mapping_entries
        return display_position_mapping_html(request, context)
    save_new_position_mappings(new_mapping_entries)
    return display_position_mapping_html(request, context)


def get_new_position_mapping_entries(post_dict):
    """
    returns an array of dictionaries that contains the new position mappings that the user entered

    Keyword Argument
    post_dict -- a dictionary representation of request.POST

    Return
    new_mapping_entries -- the array of position mapping dictionaries
    error_message -- either the error message or None
    """
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
    """
    Ensure that the new position mappings that the user entered are valid

    Keyword Argument
    new_mapping_entries -- the array of position mapping dictionaries

    Return
    success -- indicates if any of the mappings are invalid
    error_messages -- an array of possible error messages
    """
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


def save_new_position_mappings(new_mapping_entries):
    """
    Save the mappings indicates in the array of position mapping dictionaries

    Keyword Argument
    new_mapping_entries -- the array of position mapping dictionaries

    """
    for new_mapping in new_mapping_entries:
        position_name = new_mapping[Constants.position_name]
        position_index = new_mapping[Constants.position_index]
        position_email = new_mapping[Constants.position_email]
        OfficerEmailListAndPositionMapping(position_name=position_name,
                                           position_index=position_index,
                                           email=position_email).save()


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
