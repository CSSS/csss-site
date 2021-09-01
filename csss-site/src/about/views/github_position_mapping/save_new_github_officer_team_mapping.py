import logging

from django.conf import settings
from django.shortcuts import render
from querystring_parser import parser

from about.models import OfficerEmailListAndPositionMapping
from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from about.views.position_mapping_helper import update_context, POSITION_INDEX_KEY, \
    extract_valid_officers_positions_selected_for_github_team, \
    GITHUB_TEAM__TEAM_NAME_KEY, TEAM_NAME_KEY, GITHUB_TEAM_RELEVANT_PREVIOUS_TERM_KEY, \
    validate_position_names_for_github_team
from csss.views.request_validation import verify_access_logged_user_and_create_context
from csss.views_helper import ERROR_MESSAGE_KEY, ERROR_MESSAGES_KEY
from resource_management.models import OfficerPositionGithubTeam, OfficerPositionGithubTeamMapping
from resource_management.views.get_officer_list import get_list_of_officer_details_from_past_specified_terms
from resource_management.views.resource_apis.github.github_api import GitHubAPI

UNSAVED_GITHUB_OFFICER_TEAM_NAME_MAPPINGS_KEY = 'unsaved_github_officer_team_name_mapping'
OFFICER_POSITIONS = 'officer_positions'

logger = logging.getLogger('csss_site')


def save_new_github_officer_team_mapping(request):
    logger.info(f"[about/save_new_github_officer_team_mapping.py save_new_github_officer_team_mapping()] "
                f"request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request,
                                                                                          TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = f'{error_message}<br>'
        return render_value
    context[ERROR_MESSAGES_KEY] = []

    if request.method == "POST":
        post_dict = parser.parse(request.POST.urlencode())
        if 'create_new_github_mapping' in post_dict:
            context[UNSAVED_GITHUB_OFFICER_TEAM_NAME_MAPPINGS_KEY], \
                context[ERROR_MESSAGES_KEY] = _create_new_github_mapping(post_dict)
            if context[UNSAVED_GITHUB_OFFICER_TEAM_NAME_MAPPINGS_KEY] is None:
                del context[UNSAVED_GITHUB_OFFICER_TEAM_NAME_MAPPINGS_KEY]

    return render(request, 'about/github_position_mapping/github_position_mapping.html', update_context(context))


def _create_new_github_mapping(post_dict):
    """
    Saves a new github team and its assign officers

    Keyword Argument
    post_dict -- the dictionary created from the POST object

    Return
    unsaved_github_officer_team_name_mappings -- the unsaved github team mapping if it was not able to save the team
    error_messages -- a list of possible error_messages

    """
    if not (GITHUB_TEAM__TEAM_NAME_KEY in post_dict):
        error_message = "No team name detected"
        logger.info(f"[about/save_new_github_officer_team_mapping.py create_new_github_mapping()] {error_message}")
        return _create_unsaved_github_officer_team_name_mappings(), [error_message]
    team_name = post_dict[GITHUB_TEAM__TEAM_NAME_KEY]
    logger.info(
        "[about/save_new_github_officer_team_mapping.py create_new_github_mapping()] "
        f"determined the team name to be {team_name}"
    )

    if not (
            GITHUB_TEAM_RELEVANT_PREVIOUS_TERM_KEY in post_dict and
            f"{post_dict[GITHUB_TEAM_RELEVANT_PREVIOUS_TERM_KEY]}".lstrip('-').isdigit()
    ):
        error_message = "No valid relevant previous terms detected"
        logger.info(f"[about/save_new_github_officer_team_mapping.py create_new_github_mapping()] {error_message}")
        return _create_unsaved_github_officer_team_name_mappings(team_name), [error_message]

    relevant_previous_terms = f"{post_dict[GITHUB_TEAM_RELEVANT_PREVIOUS_TERM_KEY]}"
    relevant_previous_terms = 0 - int(relevant_previous_terms.lstrip('-')) if relevant_previous_terms[0] == '-' \
        else int(relevant_previous_terms)

    if not (relevant_previous_terms >= 0):
        error_message = "No valid relevant previous terms detected"
        logger.info(f"[about/save_new_github_officer_team_mapping.py create_new_github_mapping()] {error_message}")
        return _create_unsaved_github_officer_team_name_mappings(
            team_name, relevant_previous_terms=relevant_previous_terms), [error_message]

    success, error_message, officer_position_names = extract_valid_officers_positions_selected_for_github_team(
        post_dict)
    if not success:
        return \
            _create_unsaved_github_officer_team_name_mappings(
                team_name, relevant_previous_terms=relevant_previous_terms,
                officer_position_names=officer_position_names), [error_message]

    success, error_message = _validate_position_names_and_team_name_for_new_github_team(
        officer_position_names, team_name)
    if not success:
        return \
            _create_unsaved_github_officer_team_name_mappings(
                team_name, relevant_previous_terms=relevant_previous_terms,
                officer_position_names=officer_position_names), [error_message]
    logger.info(
        "[about/save_new_github_officer_team_mapping.py create_new_github_mapping()] "
        f"all specified officer and team name for github team {team_name} passed validation"
    )
    logger.info(
        "[about/save_new_github_officer_team_mapping.py create_new_github_mapping()] "
        "determined the officer position names that need to be assigned"
        f" to new github team are {officer_position_names}"
    )

    return None, \
        _save_new_github_team_mapping(officer_position_names, team_name, relevant_previous_terms)


def _create_unsaved_github_officer_team_name_mappings(
        team_name="", officer_position_names=None, relevant_previous_terms=0):
    """
    Created a dictionary that contains the user input for the github team mapping that failed validation

    Keyword Argument
    team_name -- the name of the github team
    officer_position_names -- the officer position names that the user selected
    relevant_previous_terms -- how many previous terms apply to the github team
    """
    if officer_position_names is None:
        officer_position_names = []
    position_mapping_for_selected_officer = OfficerEmailListAndPositionMapping.objects.all().order_by(
        'position_index').exclude(marked_for_deletion=True)
    unsaved_github_officer_team_name_mappings = {
        TEAM_NAME_KEY: team_name,
        OFFICER_POSITIONS: [],
        "relevant_previous_terms": relevant_previous_terms
    }
    for position in position_mapping_for_selected_officer:
        unsaved_github_officer_team_name_mappings[OFFICER_POSITIONS].append(
            {
                "position_name": position.position_name,
                POSITION_INDEX_KEY: position.position_index,
                'checked': position.position_name in officer_position_names
            }
        )
    logger.info(
        f"[about/save_new_github_officer_team_mapping.py _create_unsaved_github_officer_team_name_mappings()] "
        f"UNSAVED_GITHUB_OFFICER_TEAM_NAME_MAPPINGS : {unsaved_github_officer_team_name_mappings}"
    )
    return unsaved_github_officer_team_name_mappings


def _validate_position_names_and_team_name_for_new_github_team(officer_position_names, team_name):
    """
    ensures that the specified position_names and team name can be used for a brand new mapping by ensuring
    that there is no mapping that already exists for the team_name and all the specified position_names
    are valid and map to a position mapping

    Keyword Arguments
    officer_position_names -- the list of officer positions that need to be mapped to the team name
    team_name -- the name to be used for the github team

    Return
    Success -- Bool to indicate if the team name and position_names are validated
    error_message -- the error message
    """
    success, error_message = validate_position_names_for_github_team(officer_position_names)
    if not success:
        return success, error_message
    if len(OfficerPositionGithubTeam.objects.all().filter(team_name=team_name)) == 0:
        logger.info(
            "[about/save_new_github_officer_team_mapping.py "
            "_validate_position_names_and_team_name_for_new_github_team()]"
            " successful validation")
        return True, None
    else:
        error_message = f"There is already a github team mapping for {team_name}"
        logger.info(
            "[about/save_new_github_officer_team_mapping.py "
            "_validate_position_names_and_team_name_for_new_github_team()]"
            f" {error_message}")
        return False, error_message


def _save_new_github_team_mapping(officer_position_names, team_name, relevant_previous_terms):
    """
    save the specified github team mapping as well as try to save all the applicable officers under that team

    Keyword Argument
    officer_position_names -- the position_name for the officer position
    team_name -- the name for the new github team

    Return
    error_messages -- the list of possible error messages
    """
    success, error_message, officer_position_mappings = \
        _get_position_mappings_assigned_to_specified_positions_names(officer_position_names)
    if not success:
        return [error_message]

    github_team = OfficerPositionGithubTeam(team_name=team_name, relevant_previous_terms=relevant_previous_terms)
    github_team.save()
    logger.info("[about/save_new_github_officer_team_mapping.py _save_new_github_team_mapping()] "
                f"OfficerPositionGithubTeam object saved for team {team_name}")
    for position_mapping_obj in officer_position_mappings:
        OfficerPositionGithubTeamMapping(
            github_team=github_team, officer_position_mapping=position_mapping_obj
        ).save()
        logger.info("[about/save_new_github_officer_team_mapping.py _save_new_github_team_mapping()] "
                    f"OfficerPositionGithubTeamMapping object saved for team {team_name} and officer "
                    f"{position_mapping_obj}")
    github = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
    success, error_message = github.create_team(team_name)
    if not success:
        return [error_message]

    officer_github_usernames = get_list_of_officer_details_from_past_specified_terms(
        relevant_previous_terms=relevant_previous_terms, position_names=officer_position_names,
        filter_by_github=True
    )
    logger.info(
        "[about/save_new_github_officer_team_mapping.py "
        "_save_new_github_team_mapping()] officer_github_usernames"
        f" = {officer_github_usernames}"
    )
    error_messages = []
    for officer_github_username in officer_github_usernames:
        success, error_message = github.add_users_to_a_team([officer_github_username], team_name)
        if not success:
            error_messages.append(error_message)
    return error_messages


def _get_position_mappings_assigned_to_specified_positions_names(officer_position_names):
    """
    Returns all officer_mappings that map to the specified position_names

    Keyword Argument
    officer_position_names -- the position_name for the required OfficerEmailListAndPositionMapping object

    Return
    success -- bool to Success, turns false if one of the officer position_names is not valid
    error_message -- error_message if not successful
    officer_position_and_github_mapping -- the OfficerEmailListAndPositionMapping object that maps
     to the specified officer position names
    """
    officer_position_mappings = []
    for officer_position_name in officer_position_names:
        officer_position_mapping = OfficerEmailListAndPositionMapping.objects.all().filter(
            position_name=officer_position_name
        )
        if len(officer_position_mapping) == 0:
            error_message = f"No officer found for position with position_name {officer_position_name}"
            logger.info(
                "[about/officer_management_helper.py "
                f"_get_position_mappings_assigned_to_specified_positions_names()] {error_message}"
            )
            return False, f"{error_message}", None
        officer_position_mappings.append(officer_position_mapping[0])
    logger.info(
        "[about/officer_management_helper.py "
        "_get_position_mappings_assigned_to_specified_positions_names()]"
        f" officer_position_mappings = {officer_position_mappings}"
    )
    return True, None, officer_position_mappings
