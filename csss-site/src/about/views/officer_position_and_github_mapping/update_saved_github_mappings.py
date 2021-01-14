import logging

from django.conf import settings
from django.shortcuts import render
from querystring_parser import parser

from about.models import OfficerEmailListAndPositionMapping, Officer
from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from about.views.officer_position_and_github_mapping.save_new_github_officer_team_mapping import \
    GITHUB_TEAM__TEAM_NAME_KEY
from about.views.position_mapping_helper import update_context, \
    extract_valid_officers_positions_selected_for_github_team, GITHUB_TEAM__ID_KEY, \
    GITHUB_TEAM_RELEVANT_PREVIOUS_TERM_KEY, validate_position_names_for_github_team
from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY, ERROR_MESSAGES_KEY, \
    get_past_x_term_obj
from resource_management.models import OfficerPositionGithubTeam, OfficerPositionGithubTeamMapping
from resource_management.views.resource_apis.github.github_api import GitHubAPI

logger = logging.getLogger('csss_site')


def update_saved_github_mappings(request):
    logger.info(
        "[about/position_mapping_helper.py officer_position_and_github_mapping()]"
        f" request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request,
                                                                                          TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = f'{error_message}<br>'
        return render_value
    context[ERROR_MESSAGES_KEY] = []
    if request.method == "POST":
        post_dict = parser.parse(request.POST.urlencode())
        if "un_delete_github_mapping" in post_dict:
            context[ERROR_MESSAGES_KEY] = _toggle_deletion_status_for_github_mapping(post_dict, False)
        elif "mark_for_deletion_github_mapping" in post_dict:
            context[ERROR_MESSAGES_KEY] = _toggle_deletion_status_for_github_mapping(post_dict, True)
        elif "update_github_mapping" in post_dict:
            context[ERROR_MESSAGES_KEY] = _update_github_mapping(post_dict)
        elif "delete_github_mapping" in post_dict:
            context[ERROR_MESSAGES_KEY] = _delete_github_mapping(post_dict)

    return render(request, 'about/position_mapping/position_mapping.html', update_context(context))


def _toggle_deletion_status_for_github_mapping(post_dict, delete):
    """
    Marking a github team for deletion

    Keyword Argument
    post_dict -- the dictionary created from the POST object
    delete -- bool that indicate if the github team should be marked for deletion

    Return
    error_messages -- a list of the possible error messages
    """
    error_messages = []
    if not (GITHUB_TEAM__ID_KEY in post_dict and f"{post_dict[GITHUB_TEAM__ID_KEY]}".isdigit() and len(
            OfficerPositionGithubTeam.objects.filter(id=int(post_dict[GITHUB_TEAM__ID_KEY]))) > 0):
        error_message = "No valid team id detected"
        logger.info(f"[about/position_mapping_helper.py mark_for_deletion_github_mapping()] {error_message}")
        error_messages.append(error_message)
        return error_messages

    github_team = OfficerPositionGithubTeam.objects.get(id=int(post_dict[GITHUB_TEAM__ID_KEY]))
    github_team.marked_for_deletion = delete
    github_team.save()
    logger.info(
        "[about/position_mapping_helper.py mark_for_deletion_github_mapping()] github_team"
        f" {github_team.team_name} has been marked for deletion"
    )
    return error_messages


def _update_github_mapping(post_dict):
    """
    Updates a github mapping. This includes its name and the officer positions assigned to it

    Keyword Argument
    post_dict -- the dictionary created from the POST object

    Return
    ERROR_MESSAGES -- the list of possible error messages
    """
    success, error_message, officer_position_names = \
        extract_valid_officers_positions_selected_for_github_team(post_dict)
    if not success:
        logger.info(f"[about/position_mapping_helper.py _update_github_mapping()] {error_message}")
        return [error_message]

    success, error_message = validate_position_names_for_github_team(officer_position_names)
    if not success:
        return [error_message]

    if not (GITHUB_TEAM__TEAM_NAME_KEY in post_dict):
        error_message = "No valid team name detected"
        logger.info(f"[about/position_mapping_helper.py _update_github_mapping()] {error_message}")
        return [error_message]

    if not (GITHUB_TEAM__ID_KEY in post_dict and f"{post_dict[GITHUB_TEAM__ID_KEY]}".isdigit() and len(
            OfficerPositionGithubTeam.objects.all().filter(id=int(post_dict[GITHUB_TEAM__ID_KEY]))) > 0):
        error_message = "No valid team id detected"
        logger.info(f"[about/position_mapping_helper.py _update_github_mapping()] {error_message}")
        return [error_message]

    if not (
            GITHUB_TEAM_RELEVANT_PREVIOUS_TERM_KEY in post_dict and
            f"{post_dict[GITHUB_TEAM_RELEVANT_PREVIOUS_TERM_KEY]}".lstrip('-').isdigit()
    ):
        error_message = "No valid relevant previous terms detected"
        logger.info(f"[about/position_mapping_helper.py create_new_github_mapping()] {error_message}")
        return [error_message]

    relevant_previous_terms = f"{post_dict[GITHUB_TEAM_RELEVANT_PREVIOUS_TERM_KEY]}"
    relevant_previous_terms = 0 - int(relevant_previous_terms.lstrip('-')) if relevant_previous_terms[0] == '-' \
        else int(relevant_previous_terms)

    if not (relevant_previous_terms >= 0):
        error_message = "No valid relevant previous terms detected"
        logger.info(f"[about/position_mapping_helper.py create_new_github_mapping()] {error_message}")
        return [error_message]

    logger.info(
        "[about/position_mapping_helper.py _update_github_mapping()] officer_position_names :"
        f" {officer_position_names}"
    )

    logger.info(
        "[about/position_mapping_helper.py _update_github_mapping()] relevant_previous_terms :"
        f" {relevant_previous_terms}"
    )
    new_github_team_name = post_dict[GITHUB_TEAM__TEAM_NAME_KEY]
    logger.info(
        f"[about/position_mapping_helper.py _update_github_mapping()] new_github_team_name : {new_github_team_name}")

    github_team_db_obj = OfficerPositionGithubTeam.objects.get(id=int(post_dict[GITHUB_TEAM__ID_KEY]))
    github_api = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
    if github_team_db_obj.team_name != new_github_team_name:
        success, error_message = github_api.rename_team(github_team_db_obj.team_name, new_github_team_name)
        if not success:
            return [error_message]
        github_team_db_obj.team_name = new_github_team_name
        github_team_db_obj.relevant_previous_terms = relevant_previous_terms
        github_team_db_obj.save()

    terms = get_past_x_term_obj(relevant_previous_terms=relevant_previous_terms)

    officer_position_names_need_github_team_access_revoked = \
        _get_names_for_officer_positions_that_need_access_revoked(
            github_team_db_obj,
            officer_position_names
        )
    officer_position_names_grant_github_team_access = \
        _get_names_for_officer_positions_that_need_access_granted(github_team_db_obj, officer_position_names)

    error_messages = []

    success, returned_error_messages = _revoke_officer_with_specified_names_access_to_specified_github_team(
        github_team_db_obj, github_api, terms, officer_position_names_need_github_team_access_revoked
    )
    if not success:
        error_messages.extend(returned_error_messages)

    success, returned_error_messages = _grant_officers_with_specified_names_access_to_specified_github_team(
        github_team_db_obj, github_api, terms, officer_position_names_grant_github_team_access
    )
    if not success:
        error_messages.extend(returned_error_messages)

    return error_messages


def _get_names_for_officer_positions_that_need_access_revoked(github_team_db_obj, officer_position_names):
    """
    Returns a list of all the position_names that correspond to the
     officers who need to have their access to a github team revoked

    Keyword Argument
    github_team -- the github team object
    officer_position_names -- the list of officer position names that need to have access to the github team

    Return
    officer_position_names_need_github_team_access_revoked -- a list of all the position_names
     that correspond to the officers who need to have their access to a github team revoked
    """
    officer_position_with_access_to_github_team = [
        officer_position_github_mapping for officer_position_github_mapping in
        OfficerPositionGithubTeamMapping.objects.all().filter(github_team=github_team_db_obj)
    ]
    logger.info(
        "[about/position_mapping_helper.py get_officers_that_need_to_have_their_github_access_updated()]"
        " officer_github_team_mappings_who_currently_have_access_to_github_team ="
        f" {officer_position_with_access_to_github_team}"
    )

    officer_position_names_need_github_team_access_revoked = []
    for officer_position_with_access_to_github_team in officer_position_with_access_to_github_team:
        if officer_position_with_access_to_github_team.officer_position_mapping.position_name not in \
                officer_position_names:
            officer_position_names_need_github_team_access_revoked.append(
                officer_position_with_access_to_github_team.officer_position_mapping.position_name)
    logger.info(
        "[about/position_mapping_helper.py get_officers_that_need_to_have_their_github_access_updated()]"
        " officer_position_names_need_github_team_access_revoked ="
        f" {officer_position_names_need_github_team_access_revoked}"
    )

    return officer_position_names_need_github_team_access_revoked


def _revoke_officer_with_specified_names_access_to_specified_github_team(
        github_team_db_obj, github_api, terms,
        officer_position_names_need_github_team_access_revoked):
    """
    Revokes the officers with the specific position names from the specified github team

    Keyword Argument
    github_team -- the github team object
    github_api -- the API object for github
    term_obj -- the term object for the current term
    officer_position_names_need_github_team_access_revoked -- list of all the position_names that correspond
     to the officers who need to have their access to a github team revoked

    Return
    success -- Bool that is true or false
    error_messages -- a list of possible error messages
    """
    error_messages = []
    github_usernames_that_have_been_revoked = []
    for term in terms:
        for position_name in officer_position_names_need_github_team_access_revoked:
            for officer_github_mapping in OfficerPositionGithubTeamMapping.objects.all().filter(
                    github_team=github_team_db_obj, officer_position_mapping__position_name=position_name):
                officer_github_mapping.delete()
                logger.info(
                    "[about/position_mapping_helper.py update_existing_github_team_mappings()] "
                    f"{position_name} deleted"
                )
            officers = Officer.objects.all().filter(position_name=position_name, elected_term=term)

            for officer in officers:
                if officer.github_username not in github_usernames_that_have_been_revoked:
                    github_usernames_that_have_been_revoked.append(officer.github_username)
                    success, error_message = github_api.remove_users_from_a_team([officer.github_username],
                                                                                 github_team_db_obj.team_name)
                    if not success:
                        error_messages.append(error_message)

    if len(error_messages) == 0:
        return True, None
    return False, error_messages


def _get_names_for_officer_positions_that_need_access_granted(github_team_db_obj, officer_position_names):
    """
    Returns a list of all the position_names that correspond to the officers who need to have
     their access to a github team granted

    Keyword Argument
    github_team -- the github team object
    officer_position_names -- the list of officer position names that need to have access to the github team

    Return
    officer_position_names_grant_github_team_access -- a list of all the position_names that
     correspond to the officers who need to have their access to a github team granted
    """
    position_names_for_officers_who_currently_have_access_to_github_team = [
        officer_position_github_mapping.officer_position_mapping.position_name
        for officer_position_github_mapping in
        OfficerPositionGithubTeamMapping.objects.all().filter(github_team=github_team_db_obj)]
    officer_position_names_grant_github_team_access = []
    for officer_position_name in officer_position_names:
        if officer_position_name not in position_names_for_officers_who_currently_have_access_to_github_team:
            officer_position_names_grant_github_team_access.append(officer_position_name)
    logger.info(
        "[about/position_mapping_helper.py get_officers_that_need_to_have_their_github_access_updated()] "
        "officer_position_names_grant_github_team_access = "
        f"{officer_position_names_grant_github_team_access}")

    return officer_position_names_grant_github_team_access


def _grant_officers_with_specified_names_access_to_specified_github_team(
        github_team, github_api, terms,
        officer_position_names_grant_github_team_access):
    """
    Grants access to the officers with the specific position names from the specified github team

    Keyword Argument
    github_team -- the github team object
    github_api -- the API object for github
    term_obj -- the term object for the current term
    officer_position_names_grant_github_team_access -- a list of all
     the position_names that correspond to the officers who need to have their access to a github team granted

    Return
    success -- Bool that is true or false
    error_messages -- a list of possible error messages
    """
    for position_name_for_officer_who_need_to_have_access_to_github_team_granted in \
            officer_position_names_grant_github_team_access:
        position_mapping = OfficerEmailListAndPositionMapping.objects.all().filter(
            position_name=position_name_for_officer_who_need_to_have_access_to_github_team_granted)
        if len(position_mapping) > 0:
            position_mapping = position_mapping[0]
            logger.info(
                f"[about/position_mapping_helper.py update_existing_github_team_mappings()] "
                f"saving a mapping of {position_mapping} under team {github_team}"
            )
            OfficerPositionGithubTeamMapping(github_team=github_team,
                                             officer_position_mapping=position_mapping).save()
        else:
            logger.info("[about/position_mapping_helper.py update_existing_github_team_mappings()] "
                        "unable to find a position mapping for position_name"
                        f" {position_name_for_officer_who_need_to_have_access_to_github_team_granted}")

    error_messages = []
    github_usernames_that_have_been_added = []
    for term in terms:
        for position_name_for_officer_who_need_to_have_access_to_github_team_granted in \
                officer_position_names_grant_github_team_access:
            officers = Officer.objects.all().filter(
                position_name=position_name_for_officer_who_need_to_have_access_to_github_team_granted,
                elected_term=term)
            for officer in officers:
                if officer.github_username not in github_usernames_that_have_been_added:
                    github_usernames_that_have_been_added.append(officer.github_username)
                    success, error_message = github_api.add_users_to_a_team([officer.github_username],
                                                                            github_team.team_name)
                    if not success:
                        error_messages.append(error_message)
    if len(error_messages) == 0:
        return True, None
    return False, error_messages


def _delete_github_mapping(post_dict):
    """
    Deletes the specific github team

    Keyword Argument
    post_dict -- the dictionary created from the POST object


    Return
    ERROR_MESSAGES -- the list of possible error messages
    """
    if not (GITHUB_TEAM__ID_KEY in post_dict and f"{post_dict[GITHUB_TEAM__ID_KEY]}".isdigit() and len(
            OfficerPositionGithubTeam.objects.filter(id=int(post_dict[GITHUB_TEAM__ID_KEY]))) > 0):
        error_message = "No valid team id detected"
        logger.info("[about/position_mapping_helper.py _delete_github_mapping()]"
                    f" {error_message}")
        return [error_message]
    github_team_id = int(post_dict[GITHUB_TEAM__ID_KEY])
    github_mapping = OfficerPositionGithubTeam.objects.get(id=github_team_id)
    team_name = github_mapping.team_name
    github_mapping.delete()
    logger.info(f"[about/position_mapping_helper.py _delete_github_mapping()] deleted github team {team_name}")
    GitHubAPI(settings.GITHUB_ACCESS_TOKEN).delete_team(team_name)
    return []
