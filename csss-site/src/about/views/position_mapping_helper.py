from about.models import OfficerEmailListAndPositionMapping
from csss.setup_logger import get_logger
from csss.views.views import ERROR_MESSAGES_KEY
from csss.views_helper import there_are_multiple_entries
from resource_management.models import OfficerPositionGithubTeam


GITHUB_TEAM__ID_KEY = "github_mapping__id"
SAVED_GITHUB_MAPPINGS = 'github_teams'

OFFICER_POSITION_AVAILABLE_FOR_GITHUB_MAPPINGS = 'github_position_mapping'

POSITION_INDEX_KEY = 'position_index'

SAVED_OFFICER_POSITIONS = 'saved_officer_positions'

DELETE_GITHUB_MAPPING = 'delete_github_mapping'
GITHUB_MAPPING_SELECTED_OFFICER_POSITIONS = 'github_mapping_selected_officer_positions'
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID = "officer_email_list_and_position_mapping__id"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX = "officer_email_list_and_position_mapping__position_index"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME = "officer_email_list_and_position_mapping__position_name"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS = \
    "officer_email_list_and_position_mapping__email_list_address"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__DISCORD_ROLE_NAME = \
    "officer_email_list_and_position_mapping__discord_role_name"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__GITHUB_ACCESS = 'officer_email_list_and_position_mapping__github_access'
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__GOOGLE_DRIVE_ACCESS = \
    'officer_email_list_and_position_mapping__google_drive_access'
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ELECTED_VIA_ELECTION_OFFICER = \
    "officer_email_list_and_position_mapping__elected_via_election_officer"
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EXECUTIVE_OFFICER = \
    'officer_email_list_and_position_mapping__executive_officer'
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ELECTION_OFFICER = \
    'officer_email_list_and_position_mapping__election_officer'
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__SFSS_COUNCIL_REP = \
    'officer_email_list_and_position_mapping__sfss_council_representative'
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__FROSH_WEEK_CHAIR = \
    'officer_email_list_and_position_mapping__frosh_week_chair'
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__DISCORD_MANAGER = 'officer_email_list_and_position_mapping__discord_manager'
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__NUMBER_OF_TERMS = 'officer_email_list_and_position_mapping__number_of_terms'
OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__STARTING_MONTH = 'officer_email_list_and_position_mapping__starting_month'

OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__DELETE_STATUS = \
    "officer_email_list_and_position_mapping__delete_status"
GITHUB_TEAM__TEAM_NAME_KEY = "github_mapping__team_name"
GITHUB_TEAM_RELEVANT_PREVIOUS_TERM_KEY = "github_mapping__relevant_previous_terms"
TEAM_NAME_KEY = 'team_name'

logger = get_logger()


def update_context(context):
    context.update({
        'OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID': OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID,
        'OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX':
            OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX,
        'OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME':
            OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME,
        'OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS':
            OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS,
        'OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ELECTED_VIA_ELECTION_OFFICER':
            OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ELECTED_VIA_ELECTION_OFFICER,
        'GITHUB_TEAM__ID_KEY': GITHUB_TEAM__ID_KEY,
        'GITHUB_TEAM__TEAM_NAME_KEY': GITHUB_TEAM__TEAM_NAME_KEY,
        'NUMBER_OF_TERMS': OfficerEmailListAndPositionMapping.number_of_terms_choices_to_display_on_html(),
        'STARTING_MONTHS': OfficerEmailListAndPositionMapping.starting_month_choices_to_display_on_html()
    })

    position_mapping_for_selected_officer = \
        OfficerEmailListAndPositionMapping.objects.all().order_by('position_index')
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
                'relevant_previous_terms': github_position_mapping.relevant_previous_terms,
                'positions': []
            }
            selected_positions_for_mapping = [
                position_mapped_to_github_team.officer_position_mapping.position_index for
                position_mapped_to_github_team in
                github_position_mapping.officerpositiongithubteammapping_set.all()
            ]
            for position in position_mapping_for_selected_officer:
                github_team_mapping['positions'].append(
                    {
                        'id': position.id,
                        "position_name": position.position_name,
                        POSITION_INDEX_KEY: position.position_index,
                        "checked": position.position_index in selected_positions_for_mapping
                    }
                )
            github_team_mappings.append(github_team_mapping)
        context[SAVED_GITHUB_MAPPINGS] = github_team_mappings

    if ERROR_MESSAGES_KEY in context:
        error_experienced = False
        for error in context[ERROR_MESSAGES_KEY]:
            if error is not None and len(error) > 0:
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


def validate_elected_via_election_officer_status(elected_via_election_officer_status):
    """
    Validates the status selected for the attribute of elected via election officer

    Keyword Argument
    elected_via_election_officer_status -- the atribute that indicates if the position is elected via election officer

    Return
    success -- True or False if the attribute of elected via election officer is valid
    error_message -- an error_message if the attribute is not one of the valid options
    """
    if not (elected_via_election_officer_status == 'True' or elected_via_election_officer_status == 'False'):
        logger.info("[about/position_mapping_helper.py validate_elected_via_election_officer_status()] "
                    "validating for if the position is elected via election officer "
                    f"{elected_via_election_officer_status} was unsuccessful")
        return False, f"the option of elected_via_election_officer which is set to" \
                      f" {elected_via_election_officer_status} is invalid"
    return True, None


def validate_executive_officer_status(executive_officer_status):
    """
    Validates the status selected for the attribute of whether the officer is an executive officer

    Keyword Argument
    executive_officer_status -- the attribute that indicates if the position is an executive position

    Return
    success -- True or False if the attribute of whether the officer is an executive officer is valid
    error_message -- an error_message if the attribute is not one of the valid options
    """
    if not (executive_officer_status == 'True' or executive_officer_status == 'False'):
        logger.info("[about/position_mapping_helper.py validate_executive_status()] "
                    "validating for if the position is for an executive officer "
                    f"{executive_officer_status} was unsuccessful")
        return False, f"the option of executive_officer_status which is set to" \
                      f" {executive_officer_status} is invalid"
    return True, None


def validate_election_officer_status(election_officer_status):
    """
    Validates the status selected for the attribute of whether the officer is an election officer

    Keyword Argument
    election_officer_status -- the attribute that indicates if the position is an election officer position

    Return
    success -- True or False if the attribute of whether the officer is an election officer is valid
    error_message -- an error_message if the attribute is not one of the valid options
    """
    if not (election_officer_status == 'True' or election_officer_status == 'False'):
        logger.info("[about/position_mapping_helper.py validate_election_officer_status()] "
                    "validating for if the position is for an election officer "
                    f"{election_officer_status} was unsuccessful")
        return False, f"the option of election_officer_status which is set to" \
                      f" {election_officer_status} is invalid"
    return True, None


def validate_sfss_council_representative_status(sfss_council_representative_status):
    """
    Validates the status selected for the attribute of whether the officer is the SFSS Council Representative

    Keyword Argument
    sfss_council_representative_status -- the attribute that indicates if the position is an SFSS Council
     Representative

    Return
    success -- True or False if the attribute of whether the officer is an SFSS Council Representative is valid
    error_message -- an error_message if the attribute is not one of the valid options
    """
    if not (sfss_council_representative_status == 'True' or sfss_council_representative_status == 'False'):
        logger.info("[about/position_mapping_helper.py validate_sfss_council_representative_status()] "
                    "validating for if the position is for an SFSS Council Representative "
                    f"{sfss_council_representative_status} was unsuccessful")
        return False, f"the option of sfss_council_representative_status which is set to" \
                      f" {sfss_council_representative_status} is invalid"
    return True, None


def validate_frosh_week_chair_status(frosh_week_chair_status):
    """
    Validates the status selected for the attribute of whether the officer is the frosh week chair

    Keyword Argument
    frosh_week_chair_status -- the attribute that indicates if the position is the frosh week chair position

    Return
    success -- True or False if the attribute of whether the officer is the frosh week chair is valid
    error_message -- an error_message if the attribute is not one of the valid options
    """
    if not (frosh_week_chair_status == 'True' or frosh_week_chair_status == 'False'):
        logger.info("[about/position_mapping_helper.py validate_frosh_week_chair_status()] "
                    "validating for if the position is for the frosh week chair "
                    f"{frosh_week_chair_status} was unsuccessful")
        return False, f"the option of frosh_week_chair_status which is set to" \
                      f" {frosh_week_chair_status} is invalid"
    return True, None


def validate_discord_manager_status(discord_manager_status):
    """
    Validates the status selected for the attribute of whether the officer is the discord manager

    Keyword Argument
    discord_manager_status -- the attribute that indicates if the position is for the discord manager

    Return
    success -- True or False if the attribute of whether the officer is the discord manager is valid
    error_message -- an error_message if the attribute is not one of the valid options
    """
    if not (discord_manager_status == 'True' or discord_manager_status == 'False'):
        logger.info("[about/position_mapping_helper.py validate_discord_manager_status()] "
                    "validating for if the position is for the discord manager "
                    f"{discord_manager_status} was unsuccessful")
        return False, f"the option of discord_manager_status which is set to" \
                      f" {discord_manager_status} is invalid"
    return True, None


def validate_github_access(github_access):
    """
    Validates the status selected for the attribute of github access

    Keyword Argument
    github_access -- the atribute that indicates if the position has github access

    Return
    success -- True or False if the attribute of github access is valid
    error_message -- an error_message if the attribute is not one of the valid options
    """
    if not (github_access == 'True' or github_access == 'False'):
        logger.info("[about/position_mapping_helper.py validate_github_access()] "
                    "validating for if the position has github access "
                    f"{github_access} was unsuccessful")
        return False, f"the option of github access which is set to" \
                      f" {github_access} is invalid"
    return True, None


def validate_google_drive_access(google_drive_access):
    """
    Validates the status selected for the attribute of google drive access

    Keyword Argument
    google_drive_access -- the atribute that indicates if the position has google drive access

    Return
    success -- True or False if the attribute of google drive access is valid
    error_message -- an error_message if the attribute is not one of the valid options
    """
    if not (google_drive_access == 'True' or google_drive_access == 'False'):
        logger.info("[about/position_mapping_helper.py validate_google_drive_access()] "
                    "validating for if the position has google drive access "
                    f"{google_drive_access} was unsuccessful")
        return False, f"the option of google drive access which is set to" \
                      f" {google_drive_access} is invalid"
    return True, None


GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY = 'github_mapping_selected_officer_position'


def extract_valid_officers_positions_selected_for_github_team(post_dict):
    """
    extracts the officer position indices that have been selected to add to a github team

    Keyword Argument
    post_dict -- the dictionary created from the POST object that has the selected position indices
     mapped to the value "github_mapping_selected_officer_position"

    Return
    success - a bool, True if position indices were found
    error_message -- the error message if not successful, otherwise None
    officer_position_indices -- an int list of officer position indices that have been selected, if any were selected
    """
    if not (GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY in post_dict):
        error_message = "Did not find any positions that were selected"
        logger.info("[about/position_mapping_helper.py extract_valid_officers_positions_selected_for_github_team()]"
                    f" {error_message}")
        return False, error_message, None

    if there_are_multiple_entries(post_dict, GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY):
        officer_positions = [
            f"{officer_position_index}".strip()
            for officer_position_index in post_dict[GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY]
            if len(f"{officer_position_index}".strip()) > 0
        ]
        success = len(officer_positions) > 0
        logger.info(
            "[about/position_mapping_helper.py extract_valid_officers_positions_selected_for_github_team()] found "
            "multiple officer positions. Transformed "
            f"{post_dict[GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY]} to {officer_positions}"
            f" which has of {len(officer_positions)}"
        )
    else:
        officer_positions = f"{post_dict[GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY]}".strip()
        success = len(officer_positions) > 0
        officer_positions = [officer_positions]
        logger.info(
            "[about/position_mapping_helper.py extract_valid_officers_positions_selected_for_github_team()] found a "
            "single officer position index. Transformed "
            f"{post_dict[GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY]} to {officer_positions},"
            f" and has a success of {success}"
        )
    if not success:
        error_message = "No valid officer position indices detected"
        logger.info(f"[about/position_mapping_helper.py extract_valid_officers_positions_selected_for_github_team()]"
                    f" {error_message}")
        return False, error_message, None

    return True, None, officer_positions


def validate_position_names_for_github_team(officer_position_names):
    """
    Validates the position names that were specified in the user's POST call

    Keyword Argument
    officer_position_names -- the names that are in the user's POST call

    Return
    success -- bool that is true or false depending on if all the officer position names are valid
    error_message -- an error message if one of the position names are invalid
    """
    for officer_position_name in officer_position_names:
        if len(OfficerEmailListAndPositionMapping.objects.all().filter(position_name=officer_position_name)) == 0:
            error_message = f"There is no position mapped to the position name of {officer_position_name}"
            logger.info(
                "[about/position_mapping_helper.py "
                f"_validate_position_names_and_team_name_for_new_github_team()] {error_message}"
            )
            return False, error_message
    return True, None


def validate_number_of_terms(number_of_terms):
    """
    Validates the number of terms that were specified in the user's POST call

    Keyword Argument
    number_of_terms -- the number of terms that are in the user's POST call

    Return
    success -- bool that is true or false depending on if all the number of terms are valid
    error_message -- an error message if one of the number of terms are invalid
    """
    if number_of_terms not in OfficerEmailListAndPositionMapping.number_of_terms_choices_dict():
        error_message = f"Invalid number of terms of {number_of_terms} specified"
        logger.info(
            "[about/position_mapping_helper.py "
            f"validate_number_of_terms()] {error_message}"
        )
        return False, error_message
    return True, None


def validate_starting_month(starting_month):
    """
    Validates the starting months that were specified in the user's POST call

    Keyword Argument
    starting_month -- the starting months that are in the user's POST call

    Return
    success -- bool that is true or false depending on if all the starting months are valid
    error_message -- an error message if one of the starting months are invalid
    """
    if starting_month not in OfficerEmailListAndPositionMapping.starting_month_choices_dict():
        error_message = f"Invalid starting month of {starting_month} specified"
        logger.info(
            "[about/position_mapping_helper.py "
            f"validate_starting_month()] {error_message}"
        )
        return False, error_message
    return True, None
