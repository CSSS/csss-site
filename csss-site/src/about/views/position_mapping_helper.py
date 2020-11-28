import logging

from about.models import OfficerEmailListAndPositionMapping
from csss.views_helper import there_are_multiple_entries, ERROR_MESSAGES_KEY
from resource_management.models import OfficerPositionGithubTeam

logger = logging.getLogger('csss_site')


GITHUB_TEAM__ID_KEY = "github_mapping__id"
SAVED_GITHUB_MAPPINGS = 'github_teams'

GITHUB_TEAM__OFFICER_KEY = "github_mapping__officer_id"
OFFICER_POSITION_AVAILABLE_FOR_GITHUB_MAPPINGS = 'github_position_mapping'

POSITION_INDEX_KEY = 'position_index'

SAVED_OFFICER_POSITIONS = 'saved_officer_positions'

OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID = "officer_email_list_and_position_mapping__id"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX = "officer_email_list_and_position_mapping__position_index"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME = "officer_email_list_and_position_mapping__position_name"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS = "officer_email_list_and_position_mapping__email_list_address"
GITHUB_TEAM__TEAM_NAME_KEY = "github_mapping__team_name"

TEAM_NAME_KEY = 'team_name'


def update_context(context):
    context.update({
        'OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID': OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID,
        'OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX': OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX,
        'OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME': OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME,
        'OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS': OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS,
        'GITHUB_TEAM__ID_KEY': GITHUB_TEAM__ID_KEY,
        'GITHUB_TEAM__OFFICER_KEY': GITHUB_TEAM__OFFICER_KEY,
        'GITHUB_TEAM__TEAM_NAME_KEY': GITHUB_TEAM__TEAM_NAME_KEY,
    })


    position_mapping_for_selected_officer = OfficerEmailListAndPositionMapping.objects.all().order_by('position_index')
    if len(position_mapping_for_selected_officer) > 0:
        context[SAVED_OFFICER_POSITIONS] = position_mapping_for_selected_officer

    position_mapping_for_selected_officer = OfficerEmailListAndPositionMapping.objects.all().order_by(
        'position_index').exclude(marked_for_deletion=True)
    if len(position_mapping_for_selected_officer) > 0:
        context[OFFICER_POSITION_AVAILABLE_FOR_GITHUB_MAPPINGS] = position_mapping_for_selected_officer

    github_position_mappings = OfficerPositionGithubTeam.objects.all().order_by('id')
    if len(github_position_mappings) > 0:
        github_team_mappings = []
        for github_position_mapping in github_position_mappings:
            github_team_mapping = {
                'team_id': github_position_mapping.id,
                TEAM_NAME_KEY: github_position_mapping.team_name,
                'marked_for_deletion': github_position_mapping.marked_for_deletion,
                'positions': []
            }
            selected_positions_for_mapping = [
                position_mapped_to_github_team.officer_position_mapping.position_index for
                position_mapped_to_github_team in
                github_position_mapping.officerpositiongithubteammappingnew_set.all()
            ]
            for position in position_mapping_for_selected_officer:
                github_team_mapping['positions'].append(
                    {
                        "position_name": position.position_name,
                        POSITION_INDEX_KEY: position.position_index,
                        "checked": position.position_index in selected_positions_for_mapping
                    }
                )
            github_team_mappings.append(github_team_mapping)
        context[SAVED_GITHUB_MAPPINGS] = github_team_mappings

    error_experienced = False
    for error in context[ERROR_MESSAGES_KEY]:
        if error is not None:
            error_experienced = True

    if not error_experienced or len(context[ERROR_MESSAGES_KEY]) == 0:
        del context[ERROR_MESSAGES_KEY]

    return context


def validate_position_index(position_index, submitted_position_indices=None):
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
    if submitted_position_indices is None:
        submitted_position_indices = []
    if len(OfficerEmailListAndPositionMapping.objects.all().filter(
            position_index=position_index)) > 0 or position_index in submitted_position_indices:
        logger.info(f"[about/position_mapping_helper.py validate_position_index()] validate for position index "
                    f"{position_index} was unsuccessful")
        return False, f"Another Position already has an index of {position_index}"
    logger.info(f"[about/position_mapping_helper.py validate_position_index()] validate for position index "
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
        logger.info(f"[about/position_mapping_helper.py validate_position_name()] validate for position name "
                    f"{position_name} was unsuccessful")
        return False, f"the position of {position_name} already exists"
    logger.info(f"[about/position_mapping_helper.py validate_position_name()] validate for position name "
                f"{position_name} was successful")
    return True, None

GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY = 'github_mapping_selected_officer_position'


def extract_valid_officers_indices_selected_for_github_team(post_dict):
    """
    extracts the officer position indices that have been selected to add to a github team

    Keyword Argument
    post_dict -- the dictionary created from the POST object that has the selected position indices mapped to the value
    "github_mapping_selected_officer_position"

    Return
    success - a bool, True if position indices were found
    error_message -- the error message if not successful, otherwise None
    officer_position_indices -- an int list of officer position indices that have been selected, if any were selected
    """
    if not (GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY in post_dict):
        error_message = "Did not find any positions that were selected"
        logger.info(f"[about/position_mapping_helper.py create_new_github_mapping()] {error_message}")
        return False, error_message, None
    for officer_position_index in post_dict[GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY]:
        if not f"{officer_position_index}".isdigit():
            error_message = "Invalid position ID detected"
            logger.info(f"[about/position_mapping_helper.py create_new_github_mapping()] {error_message}")
            return False, error_message, None

    officer_position_indices = []
    if there_are_multiple_entries(post_dict, GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY):
        officer_position_indices = [int(officer_position_index) for officer_position_index in
                                    post_dict[GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY]]
        logger.info(
            f"[about/position_mapping_helper.py extract_officers_selected_for_github_team()] found multiple officer position indices. Transformed {post_dict[GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY]} to {officer_position_indices} which has of {len(officer_position_indices)}"
        )
        success = len(officer_position_indices) > 0
    else:
        if f"{post_dict[GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY]}".isdigit():
            officer_position_indices = [int(post_dict[GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY])]
            success = True
        else:
            success = False
        logger.info(
            f"[about/position_mapping_helper.py extract_officers_selected_for_github_team()] found a single officer position index. Transformed {post_dict[GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY]} to {officer_position_indices}, and has a success of {success}")
    if not success:
        error_message = "No valid officer position indices detected"
        logger.info(f"[about/position_mapping_helper.py create_new_github_mapping()] {error_message}")
        return False, error_message, None

    return True, None, officer_position_indices

def validate_select_officer_position_indices(officer_position_indices):
    """
    Verifies that a github mapping with the specified id for the team and officer_position indices exists

    Keyword Argument
    github_team_id -- the id for the OfficerPositionGithubTeam object
    officer_position_indices -- the position_index for the required OfficerEmailListAndPositionMapping object

    Return
    success -- Bool where true is returned if there exists a mapping for github_team_id and all the specified
        officer position_indices exist
    error_message -- returns an error message if there is one, or None otherwise
    """
    for officer_position_index in officer_position_indices:
        if len(OfficerEmailListAndPositionMapping.objects.all().filter(position_index=officer_position_index)) == 0:
            error_message = f"validation for position index {officer_position_index} was unsuccessful"
            logger.info(f"[about/position_mapping_helper.py validate_update_to_github_team_mapping()] {error_message}")
            return False, error_message
    return True, None
