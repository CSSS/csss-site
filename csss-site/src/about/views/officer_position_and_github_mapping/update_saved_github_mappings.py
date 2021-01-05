import logging

from django.conf import settings
from django.shortcuts import render

from about.models import OfficerEmailListAndPositionMapping, Term, Officer
from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from about.views.officer_position_and_github_mapping.save_new_github_officer_team_mapping import \
    GITHUB_TEAM__TEAM_NAME_KEY
from about.views.position_mapping_helper import update_context, \
    extract_valid_officers_indices_selected_for_github_team
from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY, ERROR_MESSAGES_KEY, \
    get_current_term
from querystring_parser import parser

from resource_management.models import OfficerPositionGithubTeam, OfficerPositionGithubTeamMappingNew
from resource_management.views.resource_apis.github.github_api import GitHubAPI

GITHUB_TEAM__ID_KEY = "github_mapping__id"

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
        if 'un_delete_github_mapping' in post_dict:
            context[ERROR_MESSAGES_KEY] = toggle_deletion_status_for_github_mapping(post_dict, False)
        elif 'mark_for_deletion_github_mapping' in post_dict:
            context[ERROR_MESSAGES_KEY] = toggle_deletion_status_for_github_mapping(post_dict, False)
        elif 'update_github_mapping' in post_dict:
            context[ERROR_MESSAGES_KEY] = update_github_mapping(post_dict)
        elif 'delete_github_mapping' in post_dict:
            context[ERROR_MESSAGES_KEY] = delete_github_mapping(post_dict)

    return render(request, 'about/position_mapping/position_mapping.html', update_context(context))


def toggle_deletion_status_for_github_mapping(post_dict, delete):
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


def update_github_mapping(post_dict):
    """
    Updates a github mapping. This includes its name and the officer positions assigned to it

    Keyword Argument
    post_dict -- the dictionary created from the POST object

    Return
    ERROR_MESSAGES -- the list of possible error messages
    """
    error_messages = []
    success, officer_position_indices = extract_valid_officers_indices_selected_for_github_team(post_dict)
    if not success:
        error_message = "No valid officer position index detected"
        error_messages.append(error_message)
        logger.info(f"[about/position_mapping_helper.py update_github_mapping()] {error_message}")
        return error_messages
    if not (GITHUB_TEAM__TEAM_NAME_KEY in post_dict):
        error_message = "No valid team name detected"
        error_messages.append(error_message)
        logger.info(f"[about/position_mapping_helper.py update_github_mapping()] {error_message}")
        return error_messages
    if not (GITHUB_TEAM__ID_KEY in post_dict and f"{post_dict[GITHUB_TEAM__ID_KEY]}".isdigit() and len(
            OfficerPositionGithubTeam.objects.all().filter(id=int(post_dict[GITHUB_TEAM__ID_KEY]))) > 0):
        error_message = "No valid team id detected"
        error_messages.append(error_message)
        logger.info(f"[about/position_mapping_helper.py update_github_mapping()] {error_message}")
        return error_messages

    logger.info(
        "[about/position_mapping_helper.py update_github_mapping()] officer_position_indices :"
        f" {officer_position_indices}"
    )
    new_github_team_name = post_dict[GITHUB_TEAM__TEAM_NAME_KEY]
    logger.info(
        f"[about/position_mapping_helper.py update_github_mapping()] new_github_team_name : {new_github_team_name}")

    github_team_db_obj = OfficerPositionGithubTeam.objects.get(id=int(post_dict[GITHUB_TEAM__ID_KEY]))
    github_api = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
    if github_team_db_obj.team_name != new_github_team_name:
        success, error_message = github_api.rename_team(github_team_db_obj.team_name, new_github_team_name)
        if not success:
            error_messages.extend(error_message)
            return error_messages
        github_team_db_obj.team_name = new_github_team_name
        github_team_db_obj.save()

    current_term = get_current_term()
    terms_obj = Term.objects.filter(term_number=current_term)
    if len(terms_obj) == 0:
        error_message = f"no terms exist for current term of {current_term}"
        logger.info(f"[about/position_mapping_helper.py update_existing_github_team_mappings()] {error_message}")
        return False, False, [error_message]
    term_obj = terms_obj[0]

    success, returned_error_messages = revoke_officer_with_specified_indices_access_to_specified_github_team(
        github_team_db_obj, github_api, term_obj,
        get_indices_for_officer_positions_that_need_access_revoked(
            github_team_db_obj,
            officer_position_indices)
    )
    if not success:
        error_messages.extend(returned_error_messages)
    success, returned_error_messages = grant_officers_with_specified_indices_access_to_specified_github_team(
        github_team_db_obj, github_api, term_obj,
        get_indices_for_officer_positions_that_need_access_granted(
            github_team_db_obj,
            officer_position_indices)
    )
    if not success:
        error_messages.extend(returned_error_messages)
    return error_messages


def get_indices_for_officer_positions_that_need_access_revoked(github_team_db_obj, officer_position_indices):
    """
    Returns a list of all the position_indices that correspond to the
     officers who need to have their access to a github team revoked

    Keyword Argument
    github_team -- the github team object
    officer_position_indices -- the list of officer position indices that need to have access to the github team

    Return
    officer_position_indices_need_github_team_access_revoked -- a list of all the position_indices
     that correspond to the officers who need to have their access to a github team revoked
    """
    officer_position_indices_with_access_to_github_team = [
        officer for officer in
        OfficerPositionGithubTeamMappingNew.objects.all().filter(github_team=github_team_db_obj)
    ]
    logger.info(
        "[about/position_mapping_helper.py get_officers_that_need_to_have_their_github_access_updated()]"
        " officer_github_team_mappings_who_currently_have_access_to_github_team ="
        f" {officer_position_indices_with_access_to_github_team}"
    )

    officer_position_indices_need_github_team_access_revoked = []
    for officer_position_index_with_access_to_github_team in officer_position_indices_with_access_to_github_team:
        if officer_position_index_with_access_to_github_team.officer_position_mapping.position_index not in \
                officer_position_indices:
            officer_position_indices_need_github_team_access_revoked.append(
                officer_position_index_with_access_to_github_team.officer_position_mapping.position_index)
    logger.info(
        "[about/position_mapping_helper.py get_officers_that_need_to_have_their_github_access_updated()]"
        " position_indices_for_officers_who_need_to_have_access_to_github_team_revoked ="
        f" {officer_position_indices_need_github_team_access_revoked}"
    )

    return officer_position_indices_need_github_team_access_revoked


def revoke_officer_with_specified_indices_access_to_specified_github_team(
        github_team_db_obj, github_api, term_obj,
        officer_position_indices_need_github_team_access_revoked):
    """
    Revokes the officers with the specific position indices from the specified github team

    Keyword Argument
    github_team -- the github team object
    github_api -- the API object for github
    term_obj -- the term object for the current term
    officer_position_indices_need_github_team_access_revoked -- list of all the position_indices that correspond
     to the officers who need to have their access to a github team revoked

    Return
    success -- Bool that is true or false
    error_messages -- a list of possible error messages
    """
    error_messages = []
    for position_index in officer_position_indices_need_github_team_access_revoked:
        for officer_github_mapping in OfficerPositionGithubTeamMappingNew.objects.all().filter(
                github_team=github_team_db_obj, officer_position_mapping__position_index=position_index):
            officer_github_mapping.delete()
            logger.info(
                f"[about/position_mapping_helper.py update_existing_github_team_mappings()] {position_index} deleted")
        officers = Officer.objects.all().filter(position_index=position_index, elected_term=term_obj)

        if len(officers) > 0:
            success, error_message = github_api.remove_users_from_a_team([officers[0].github_username],
                                                                         github_team_db_obj.team_name)
            if not success:
                error_messages.append(error_message)
        else:
            logger.info(
                "[about/position_mapping_helper.py update_existing_github_team_mappings()]"
                f" unable to find officer under term {term_obj} for position_index {position_index}"
            )

    if len(error_messages) == 0:
        return True, None
    return False, error_messages


def get_indices_for_officer_positions_that_need_access_granted(github_team_db_obj, officer_position_indices):
    """
    Returns a list of all the position_indices that correspond to the officers who need to have
     their access to a github team granted

    Keyword Argument
    github_team -- the github team object
    officer_position_indices -- the list of officer position indices that need to have access to the github team

    Return
    officer_position_indices_grant_github_team_access -- a list of all the position_indices that
     correspond to the officers who need to have their access to a github team granted
    """
    position_indices_for_officers_who_currently_have_access_to_github_team = [
        officer.officer_position_mapping.position_index for officer in
        OfficerPositionGithubTeamMappingNew.objects.all().filter(github_team=github_team_db_obj)]
    officer_position_indices_grant_github_team_access = []
    for officer_position_index in officer_position_indices:
        if officer_position_index not in position_indices_for_officers_who_currently_have_access_to_github_team:
            officer_position_indices_grant_github_team_access.append(officer_position_index)
    logger.info(
        "[about/position_mapping_helper.py get_officers_that_need_to_have_their_github_access_updated()] "
        "position_indices_for_officers_who_need_to_have_access_to_github_team_granted = "
        f"{officer_position_indices_grant_github_team_access}")

    return officer_position_indices_grant_github_team_access


def grant_officers_with_specified_indices_access_to_specified_github_team(
        github_team, github_api, term_obj,
        officer_position_indices_grant_github_team_access):
    """
    Grants access to the officers with the specific position indices from the specified github team

    Keyword Argument
    github_team -- the github team object
    github_api -- the API object for github
    term_obj -- the term object for the current term
    position_indices_for_officers_who_need_to_have_access_to_github_team_granted -- a list of all
     the position_indices that correspond to the officers who need to have their access to a github team granted

    Return
    success -- Bool that is true or false
    error_messages -- a list of possible error messages
    """
    for position_index_for_officer_who_need_to_have_access_to_github_team_granted in \
            officer_position_indices_grant_github_team_access:
        position_mapping = OfficerEmailListAndPositionMapping.objects.all().filter(
            position_index=position_index_for_officer_who_need_to_have_access_to_github_team_granted)
        if len(position_mapping) > 0:
            position_mapping = position_mapping[0]
            logger.info(
                f"[about/position_mapping_helper.py update_existing_github_team_mappings()] "
                f"saving a mapping of {position_mapping} under team {github_team}"
            )
            OfficerPositionGithubTeamMappingNew(github_team=github_team,
                                                officer_position_mapping=position_mapping).save()
        else:
            logger.info("[about/position_mapping_helper.py update_existing_github_team_mappings()] "
                        "unable to find a position mapping for position_index"
                        f" {position_index_for_officer_who_need_to_have_access_to_github_team_granted}")

    error_messages = []
    for position_index_for_officer_who_need_to_have_access_to_github_team_granted in \
            officer_position_indices_grant_github_team_access:
        officer = Officer.objects.all().filter(
            position_index=position_index_for_officer_who_need_to_have_access_to_github_team_granted,
            elected_term=term_obj)
        if len(officer) > 0:
            officer = officer[0]
            success, error_message = github_api.add_users_to_a_team([officer.github_username], github_team.team_name)
            if not success:
                error_messages.append(error_message)
        else:
            logger.info(
                "[about/position_mapping_helper.py update_existing_github_team_mappings()] "
                f"unable to find any officers for term {term_obj} and position_index "
                f"{position_index_for_officer_who_need_to_have_access_to_github_team_granted}")
    if len(error_messages) == 0:
        return True, None
    return False, error_messages


def delete_github_mapping(post_dict):
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
        logger.info("[about/position_mapping_helper.py delete_github_mapping()]"
                    f" {error_message}")
        return [error_message]
    github_team_id = int(post_dict[GITHUB_TEAM__ID_KEY])
    github_mapping = OfficerPositionGithubTeam.objects.get(id=github_team_id)
    team_name = github_mapping.team_name
    github_mapping.delete()
    logger.info(f"[about/position_mapping_helper.py delete_github_mapping()] deleted github team {team_name}")
    GitHubAPI(settings.GITHUB_ACCESS_TOKEN).delete_team(team_name)
    return []
