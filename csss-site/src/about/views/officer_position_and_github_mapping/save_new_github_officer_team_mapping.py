import logging

from django.conf import settings
from django.shortcuts import render
from querystring_parser import parser

from about.models import OfficerEmailListAndPositionMapping, Term, Officer
from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from about.views.position_mapping_helper import update_context, POSITION_INDEX_KEY, \
    extract_valid_officers_indices_selected_for_github_team, \
    GITHUB_TEAM__TEAM_NAME_KEY, TEAM_NAME_KEY
from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY, ERROR_MESSAGES_KEY, \
    get_current_term
from resource_management.models import OfficerPositionGithubTeam, OfficerPositionGithubTeamMapping
from resource_management.views.resource_apis.github.github_api import GitHubAPI

UNSAVED_GITHUB_OFFICER_TEAM_NAME_MAPPINGS_KEY = 'unsaved_github_officer_team_name_mapping'
OFFICER_POSITIONS = 'officer_positions'

logger = logging.getLogger('csss_site')


def save_new_github_officer_team_mapping(request):
    logger.info(f"[about/position_mapping_helper.py officer_position_and_github_mapping()] "
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
                context[ERROR_MESSAGES_KEY] = create_new_github_mapping(post_dict)
            if context[UNSAVED_GITHUB_OFFICER_TEAM_NAME_MAPPINGS_KEY] is None:
                del context[UNSAVED_GITHUB_OFFICER_TEAM_NAME_MAPPINGS_KEY]

    return render(request, 'about/position_mapping/position_mapping.html', update_context(context))


def create_new_github_mapping(post_dict):
    """
    Saves a new github team and its assign officers

    Keyword Argument
    post_dict -- the dictionary created from the POST object

    Return
    UNSAVED_GITHUB_OFFICER_TEAM_NAME_MAPPINGS -- the unsaved github team mapping if it was not able to save the team
    ERROR_MESSAGES -- a list of possible error_messagess

    """
    unsaved_github_officer_team_name_mappings = None
    error_messages = []
    if not (GITHUB_TEAM__TEAM_NAME_KEY in post_dict):
        error_message = "No team name detected"
        logger.info(f"[about/position_mapping_helper.py create_new_github_mapping()] {error_message}")
        error_messages.append(error_message)
        return create_unsaved_github_officer_team_name_mappings(), error_messages
    team_name = post_dict[GITHUB_TEAM__TEAM_NAME_KEY]
    logger.info(
        f"[about/position_mapping_helper.py create_new_github_mapping()] determined the team name to be {team_name}")

    success, error_message, officer_position_indices = extract_valid_officers_indices_selected_for_github_team(
        post_dict)
    if not success:
        error_messages.append(error_message)
        return \
            create_unsaved_github_officer_team_name_mappings(
                team_name, officer_position_indices=officer_position_indices
            ), error_messages

    success, error_message = validate_officer_indices_and_team_name_for_new_github_team(
        officer_position_indices, team_name)
    if not success:
        error_messages.append(error_message)
        return \
            create_unsaved_github_officer_team_name_mappings(
                team_name,
                officer_position_indices=officer_position_indices
            ), error_messages
    logger.info(
        "[about/position_mapping_helper.py create_new_github_mapping()] "
        f"all specified officer and team name for github team {team_name} passed validation"
    )
    logger.info(
        "[about/position_mapping_helper.py create_new_github_mapping()] "
        "determined the officer position indices that need to be assigned"
        f" to new github team are {officer_position_indices}"
    )

    error_messages.extend(save_new_github_team_mapping(officer_position_indices, team_name))
    return unsaved_github_officer_team_name_mappings, error_messages


def create_unsaved_github_officer_team_name_mappings(team_name="", officer_position_indices=None):
    if officer_position_indices is None:
        officer_position_indices = []
    position_mapping_for_selected_officer = OfficerEmailListAndPositionMapping.objects.all().order_by(
        'position_index').exclude(marked_for_deletion=True)
    unsaved_github_officer_team_name_mappings = {
        TEAM_NAME_KEY: team_name,
        OFFICER_POSITIONS: []
    }
    for position in position_mapping_for_selected_officer:
        unsaved_github_officer_team_name_mappings[OFFICER_POSITIONS].append(
            {
                "position_name": position.position_name,
                POSITION_INDEX_KEY: position.position_index,
                'checked': position.position_index in officer_position_indices
            }
        )
    logger.info(
        f"[about/position_mapping_helper.py create_new_github_mapping()] "
        f"UNSAVED_GITHUB_OFFICER_TEAM_NAME_MAPPINGS : {unsaved_github_officer_team_name_mappings}"
    )
    return unsaved_github_officer_team_name_mappings


def validate_officer_indices_and_team_name_for_new_github_team(officer_position_indices, team_name):
    """
    ensures that the specified officer_position_indices and team name can be used for a brand new mapping by ensuring
    that there is no mapping that already exists for the team_name and all the specified officer_position_indices
    are valid and map to a position mapping

    Keyword Arguments
    officer_position_indices -- the list of officers that need to be mapped to the team name
    team_name -- the name to be used for the github team

    Return
    Success -- Bool to indicate if the team name and officer_position_indices are validated
    error_message -- the error message
    """
    for officer_position_index in officer_position_indices:
        if len(OfficerEmailListAndPositionMapping.objects.all().filter(position_index=officer_position_index)) == 0:
            error_message = f"There is no position mapped to the position index of {officer_position_index}"
            logger.info(
                "[about/position_mapping_helper.py "
                f"validate_officer_indices_and_team_name_for_new_github_team()] {error_message}"
            )
            return False, error_message
    if len(OfficerPositionGithubTeam.objects.all().filter(team_name=team_name)) == 0:
        logger.info(
            "[about/position_mapping_helper.py validate_officer_indices_and_team_name_for_new_github_team()]"
            " successful validation")
        return True, None
    else:
        error_message = f"There is already a github team mapping for {team_name}"
        logger.info(
            "[about/position_mapping_helper.py validate_officer_indices_and_team_name_for_new_github_team()]"
            f" {error_message}")
        return False, error_message


def save_new_github_team_mapping(officer_position_indices, team_name):
    """
    save the specified github team mapping as well as try to save all the applicable officers under that team

    Keyword Argument
    officer_position_indices -- the position_index for the officer position
    team_name -- the name for the new github team

    Return
    error_messages -- the list of possible error messages
    """
    error_messages = []
    success, error_message, officers, position_mapping_objs = \
        get_officers_and_position_mappings_assigned_to_specified_positions_indices(
            officer_position_indices)
    if not success:
        error_messages.append(error_message)
        return error_messages
    else:
        github_team = OfficerPositionGithubTeam(team_name=team_name)
        github_team.save()
        logger.info("[about/position_mapping_helper.py save_new_github_team_mapping()] "
                    f"OfficerPositionGithubTeam object saved for team {team_name}")
        for position_mapping_obj in position_mapping_objs:
            OfficerPositionGithubTeamMapping(
                github_team=github_team, officer_position_mapping=position_mapping_obj
            ).save()
            logger.info("[about/position_mapping_helper.py save_new_github_team_mapping()] "
                        f"OfficerPositionGithubTeamMapping object saved for team {team_name} and officer "
                        f"{position_mapping_obj}")
        github = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
        success, error_message = github.create_team(team_name)
        if not success:
            error_messages.append(error_message)
            return error_messages
        else:
            for officer in officers:
                success, error_message = github.add_users_to_a_team([officer.github_username], team_name)
                if not success:
                    error_messages.append(error_message)
            return error_messages


def get_officers_and_position_mappings_assigned_to_specified_positions_indices(officer_position_indices):
    """
    Returns all officers and officer_mappings that map to the specified officer_position_indices

    Keyword Argument
    officer_position_indices -- the position_index for the required OfficerEmailListAndPositionMapping
     and Officer object

    Return
    success -- bool to Success, turns false if current term does not exist or one of the officer position_indices
     is not valid
    error_message -- error_message if not successful
    officers -- either returns the Officers object that map to specified officer_position_indices or
     None if the officer_position_indices does not map to any current Officers
    officer_position_and_github_mapping -- the OfficerEmailListAndPositionMapping object that maps
     to the specified officer position indices
    """
    current_term_number = get_current_term()
    terms_obj = Term.objects.all().filter(term_number=current_term_number)
    if len(terms_obj) == 0:
        error_message = f"No terms exist for current term of {current_term_number}"
        logger.info(
            f"[about/position_mapping_helper.py "
            f"get_officers_and_position_mappings_assigned_to_specified_positions_indices()] {error_message}"
        )
        return False, error_message, None, None
    term_obj = terms_obj[0]

    officer_position_mappings = []
    for officer_position_index in officer_position_indices:
        officer_position_mapping = OfficerEmailListAndPositionMapping.objects.all().filter(
            position_index=officer_position_index
        )
        if len(officer_position_mapping) == 0:
            error_message = f"No officer found for position with position_index {officer_position_index}"
            logger.info(
                "[about/position_mapping_helper.py "
                f"get_officers_and_position_mappings_assigned_to_specified_positions_indices()] {error_message}"
            )
            return False, f"{error_message}", None, None
        officer_position_mappings.append(officer_position_mapping[0])
    logger.info(
        "[about/position_mapping_helper.py "
        "get_officers_and_position_mappings_assigned_to_specified_positions_indices()]"
        f" officer_position_mappings = {officer_position_mappings}"
    )

    officers = []
    for officer_position_mapping in officer_position_mappings:
        officers.extend([
            officer for officer in
            Officer.objects.all().filter(
                position_index=officer_position_mapping.position_index, elected_term=term_obj
            )
        ])
    logger.info(
        "[about/position_mapping_helper.py "
        f"get_officers_and_position_mappings_assigned_to_specified_positions_indices()] officers = {officers}"
    )
    return True, None, officers, officer_position_mappings
