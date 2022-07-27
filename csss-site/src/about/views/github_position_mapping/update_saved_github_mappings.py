import logging

from django.shortcuts import render
from querystring_parser import parser

from about.models import OfficerEmailListAndPositionMapping
from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from about.views.position_mapping_helper import update_context, GITHUB_TEAM__ID_KEY, \
    GITHUB_TEAM_RELEVANT_PREVIOUS_TERM_KEY, validate_position_names_for_github_team, \
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__DELETE_STATUS, GITHUB_MAPPING_SELECTED_OFFICER_POSITIONS, \
    DELETE_GITHUB_MAPPING, GITHUB_TEAM__TEAM_NAME_KEY
from csss.views.context_creation.create_authenticated_contexts import \
    create_context_for_updating_github_mappings_and_permissions
from csss.views.privilege_validation.list_of_officer_details_from_past_specified_terms import \
    get_list_of_officer_details_from_past_specified_terms
from csss.views.views import ERROR_MESSAGES_KEY
from resource_management.models import OfficerPositionGithubTeam, OfficerPositionGithubTeamMapping
from resource_management.views.resource_apis.github.github_api import GitHubAPI

logger = logging.getLogger('csss_site')


def update_saved_github_mappings(request):
    logger.info(
        "[about/update_saved_github_mappings.py update_saved_github_mappings()]"
        f" request.POST={request.POST}"
    )
    context = create_context_for_updating_github_mappings_and_permissions(request, tab=TAB_STRING)
    context[ERROR_MESSAGES_KEY] = []
    if request.method == "POST":
        github_mappings = list(
            parser.parse(request.POST.urlencode())['saved_officer_position_github_mapping'].values()
        )
        for github_mapping in github_mappings:
            context[ERROR_MESSAGES_KEY].extend(_update_github_mapping(github_mapping))
    return render(request, 'about/github_position_mapping/github_position_mapping.html', update_context(context))


def _update_github_mapping(github_mapping):
    """
    Updates a github mapping. This includes its name and the officer positions assigned to it

    Keyword Argument
    post_dict -- the dictionary created from the POST object

    Return
    error_messages -- the list of possible error messages
    """
    if not (
            GITHUB_TEAM__ID_KEY in github_mapping and f"{github_mapping[GITHUB_TEAM__ID_KEY]}".isdigit() and
            len(OfficerPositionGithubTeam.objects.all().filter(id=int(github_mapping[GITHUB_TEAM__ID_KEY]))) == 1):
        error_message = "No valid team id detected"
        logger.info(f"[about/update_saved_github_mappings.py _update_github_mapping()] {error_message}")
        return [error_message]

    if not (GITHUB_TEAM__TEAM_NAME_KEY in github_mapping):
        error_message = "No valid team name detected"
        logger.info(f"[about/update_saved_github_mappings.py _update_github_mapping()] {error_message}")
        return [error_message]

    if not (
            GITHUB_TEAM_RELEVANT_PREVIOUS_TERM_KEY in github_mapping and
            f"{github_mapping[GITHUB_TEAM_RELEVANT_PREVIOUS_TERM_KEY]}".lstrip('-').isdigit()
    ):
        error_message = "No valid relevant previous terms detected"
        logger.info(f"[about/update_saved_github_mappings.py _update_github_mapping()] {error_message}")
        return [error_message]

    if not (OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__DELETE_STATUS in github_mapping):
        error_message = "No delete status found in request"
        logger.info(f"[about/update_saved_github_mappings.py _update_github_mapping()] {error_message}")
        return [error_message]

    if github_mapping[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__DELETE_STATUS] not in ('True', 'False'):
        error_message = "invalid delete status detected"
        logger.info(f"[about/update_saved_github_mappings.py _update_github_mapping()] {error_message}")
        return [error_message]

    if GITHUB_MAPPING_SELECTED_OFFICER_POSITIONS not in github_mapping:
        error_message = "No positions detected for github mapping"
        logger.info(f"[about/update_saved_github_mappings.py _update_github_mapping()] {error_message}")
        return [error_message]

    officer_position_names = github_mapping[GITHUB_MAPPING_SELECTED_OFFICER_POSITIONS]
    if type(officer_position_names) is not list:
        officer_position_names = [officer_position_names]

    logger.info(
        "[about/update_saved_github_mappings.py _update_github_mapping()] officer_position_names :"
        f" {officer_position_names}"
    )

    success, error_message = validate_position_names_for_github_team(officer_position_names)
    if not success:
        return [error_message]

    delete_status = github_mapping[OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__DELETE_STATUS] == 'True'

    logger.info(
        "[about/update_saved_github_mappings.py _update_github_mapping()] delete_status :"
        f" {delete_status}"
    )
    relevant_previous_terms = f"{github_mapping[GITHUB_TEAM_RELEVANT_PREVIOUS_TERM_KEY]}"
    relevant_previous_terms = 0 - int(relevant_previous_terms.lstrip('-')) if relevant_previous_terms[0] == '-' \
        else int(relevant_previous_terms)

    logger.info(
        "[about/update_saved_github_mappings.py _update_github_mapping()] relevant_previous_terms :"
        f" {relevant_previous_terms}"
    )

    if not (relevant_previous_terms >= 0):
        error_message = "No valid relevant previous terms detected"
        logger.info(f"[about/update_saved_github_mappings.py _update_github_mapping()] {error_message}")
        return [error_message]

    new_github_team_name = github_mapping[GITHUB_TEAM__TEAM_NAME_KEY]
    logger.info(
        f"[about/update_saved_github_mappings.py _update_github_mapping()] new_github_team_name: "
        f"{new_github_team_name}"
    )

    github_team_db_obj = OfficerPositionGithubTeam.objects.get(id=int(github_mapping[GITHUB_TEAM__ID_KEY]))
    github_api = GitHubAPI()
    if github_mapping[DELETE_GITHUB_MAPPING] == 'True':
        return [_delete_github_mapping(github_team_db_obj, github_api)]

    if github_team_db_obj.team_name != new_github_team_name:
        success, error_message = github_api.rename_team(github_team_db_obj.team_name, new_github_team_name)
        if not success:
            return [error_message]
        github_team_db_obj.team_name = new_github_team_name
        github_team_db_obj.save()
        logger.info(
            f"[about/update_saved_github_mappings.py _update_github_mapping()] github team name changed "
            f"to {new_github_team_name}"
        )
    if github_team_db_obj.marked_for_deletion != delete_status:
        github_team_db_obj.marked_for_deletion = delete_status
        github_team_db_obj.save()

    github_usernames_that_currently_have_access = _get_github_usernames_that_currently_have_github_access(
        github_team_db_obj, github_team_db_obj.relevant_previous_terms
    )
    logger.info(
        "[about/update_saved_github_mappings.py _update_github_mapping()] "
        "github_usernames_that_currently_have_access: "
        f" {github_usernames_that_currently_have_access}"
    )

    if github_team_db_obj.relevant_previous_terms != relevant_previous_terms:
        github_team_db_obj.relevant_previous_terms = relevant_previous_terms
        github_team_db_obj.save()
        logger.info(
            f"[about/update_saved_github_mappings.py _update_github_mapping()] github team relevant_previous_terms "
            f"changed to {relevant_previous_terms}"
        )

    github_usernames_that_need_access = _get_github_usernames_that_need_github_access_granted(
        officer_position_names, github_team_db_obj.relevant_previous_terms
    )
    logger.info(
        f"[about/update_saved_github_mappings.py _update_github_mapping()] github_usernames_that_need_access: "
        f" {github_usernames_that_need_access}"
    )

    github_usernames_need_github_access_granted = []
    github_usernames_need_github_access_revoked = []
    for github_username_that_currently_has_access in github_usernames_that_currently_have_access:
        if github_username_that_currently_has_access not in github_usernames_that_need_access:
            github_usernames_need_github_access_revoked.append(github_username_that_currently_has_access)

    logger.info(
        "[about/update_saved_github_mappings.py _update_github_mapping()] "
        "github_usernames_need_github_access_revoked: "
        f" {github_usernames_need_github_access_revoked}"
    )

    for github_username_that_need_access in github_usernames_that_need_access:
        if github_username_that_need_access not in github_usernames_that_currently_have_access:
            github_usernames_need_github_access_granted.append(github_username_that_need_access)
    logger.info(
        "[about/update_saved_github_mappings.py _update_github_mapping()] "
        "github_usernames_need_github_access_granted: "
        f" {github_usernames_need_github_access_granted}"
    )
    error_messages = []
    for github_username_need_github_access_revoked in github_usernames_need_github_access_revoked:
        success, error_message = github_api.remove_users_from_a_team([github_username_need_github_access_revoked],
                                                                     github_team_db_obj.team_name)
        if not success:
            error_messages.append(error_message)

    for github_username_need_github_access_granted in github_usernames_need_github_access_granted:
        success, error_message = github_api.add_users_to_a_team([github_username_need_github_access_granted],
                                                                github_team_db_obj.team_name)
        if not success:
            error_messages.append(error_message)

    current_officer_positions_mapped_to_github_team = [
        officer_position_github_team_mapping
        for officer_position_github_team_mapping in
        OfficerPositionGithubTeamMapping.objects.all().filter(
            github_team=github_team_db_obj
        )
    ]
    logger.info(
        "[about/update_saved_github_mappings.py _update_github_mapping()] "
        "current_officer_positions_mapped_to_github_team: "
        f" {current_officer_positions_mapped_to_github_team}"
    )
    current_officer_positions_names_mapped_to_github_team = [
        current_officer_position_mapped_to_github_team.officer_position_mapping.position_name
        for current_officer_position_mapped_to_github_team in current_officer_positions_mapped_to_github_team
    ]
    logger.info(
        "[about/update_saved_github_mappings.py _update_github_mapping()] "
        "current_officer_positions_named_mapped_to_github_team: "
        f" {current_officer_positions_names_mapped_to_github_team}"
    )
    for new_officer_position_name in officer_position_names:
        if new_officer_position_name not in current_officer_positions_names_mapped_to_github_team:
            officer_position_github_team_mapping = OfficerPositionGithubTeamMapping(
                github_team=github_team_db_obj,
                officer_position_mapping=OfficerEmailListAndPositionMapping.objects.get(
                    position_name=new_officer_position_name
                )
            )
            officer_position_github_team_mapping.save()
            logger.info(
                "[about/update_saved_github_mappings.py _update_github_mapping()] "
                "created a new officer position github team mapping: "
                f" {officer_position_github_team_mapping}"
            )
    for current_officer_position_mapped_to_github_team in current_officer_positions_mapped_to_github_team:
        if current_officer_position_mapped_to_github_team.officer_position_mapping.position_name not in \
                officer_position_names:
            logger.info(
                "[about/update_saved_github_mappings.py _update_github_mapping()] following mapping deleted "
                f" {current_officer_position_mapped_to_github_team}"
            )
            current_officer_position_mapped_to_github_team.delete()

    return error_messages


def _delete_github_mapping(github_team_db_obj, github_api):
    """
    Deletes the specific github team

    Keyword Argument
    post_dict -- the dictionary created from the POST object

    Return
    error_messages -- the list of possible error messages
    """
    logger.info(
        f"[about/update_saved_github_mappings.py _delete_github_mapping()] "
        f"deleted github team {github_team_db_obj.team_name}"
    )
    github_api.delete_team(github_team_db_obj.team_name)
    github_team_db_obj.delete()
    return []


def _get_github_usernames_that_currently_have_github_access(
        github_team_db_obj, relevant_previous_terms):
    """
    Get the github usernames that current have access to the specified github team

    Keyword Argument
    github_team_db_obj -- the OfficerPositionGithubTeam object for the github team
    relevant_previous_terms -- how far back in previous terms to look for github usernames

    Return
    github_usernames_that_currently_have_access -- github usernames that currently have access to the github team
    specified by the github_team_db_obj object
    """
    officer_position_names_that_currently_have_access_to_github_team = [
        position.officer_position_mapping.position_name
        for position in OfficerPositionGithubTeamMapping.objects.all().filter(github_team=github_team_db_obj)
    ]
    logger.info(
        "[about/update_saved_github_mappings.py _get_github_usernames_that_currently_have_github_access()]"
        " officer_position_names_that_currently_have_access_to_github_team ="
        f" {officer_position_names_that_currently_have_access_to_github_team}"
    )

    github_usernames_that_currently_have_access = get_list_of_officer_details_from_past_specified_terms(
        relevant_previous_terms=relevant_previous_terms,
        position_names=officer_position_names_that_currently_have_access_to_github_team,
        filter_by_github=True
    )
    logger.info(
        "[about/update_saved_github_mappings.py _get_github_usernames_that_currently_have_github_access()]"
        " github_usernames_that_currently_have_access ="
        f" {github_usernames_that_currently_have_access}"
    )
    return github_usernames_that_currently_have_access


def _get_github_usernames_that_need_github_access_granted(
        officer_position_names, relevant_previous_terms):
    """
    Gets the github usernames that need to have their access granted based on what their officer position_name is

    Keyword Argument
    officer_position_names -- the list of applicable officer position_names
    relevant_previous_terms -- how far back in previous terms to look for github usernames

    Return
    github_usernames_that_need_access -- the list of github usernames that match the position
     names under the relevant_previous_terms
    """
    github_usernames_that_need_access = get_list_of_officer_details_from_past_specified_terms(
        relevant_previous_terms=relevant_previous_terms, position_names=officer_position_names,
        filter_by_github=True
    )
    logger.info(
        "[about/update_saved_github_mappings.py _get_github_usernames_that_need_github_access_granted()]"
        " github_usernames_that_need_access ="
        f" {github_usernames_that_need_access}"
    )
    return github_usernames_that_need_access
