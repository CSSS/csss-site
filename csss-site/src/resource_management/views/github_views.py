import datetime
import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from about.models import Term, Officer
from resource_management.models import NonOfficerGithubMember, NaughtyOfficer, OfficerGithubTeam
from .resource_apis.github.github_api import GitHubAPI
from csss.views_helper import there_are_multiple_entries, verify_access_logged_user_and_create_context, \
    ERROR_MESSAGE_KEY

GITHUB_RECORD_KEY = 'record_id'
GITHUB_USERNAME_KEY = 'user_name'
LEGAL_NAME_KEY = 'legal_name'
GITHUB_TEAM_KEY = 'github_team'
logger = logging.getLogger('csss_site')
TAB_STRING = 'administration'


def index(request):
    """shows the main page for google drive permission management

    """
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:  # if the user accessing the page is not authorized to access it
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if ERROR_MESSAGE_KEY in request.session:
        context['error_experienced'] = request.session[ERROR_MESSAGE_KEY].split("<br>")
        del request.session[ERROR_MESSAGE_KEY]
    context['github_team'] = OfficerGithubTeam.objects.all().filter().order_by('id')
    context['non_officer_github_member'] = NonOfficerGithubMember.objects.all().filter().order_by('id')
    context['GITHUB_RECORD_KEY'] = GITHUB_RECORD_KEY
    context['GITHUB_USERNAME_KEY'] = GITHUB_USERNAME_KEY
    context['LEGAL_NAME_KEY'] = LEGAL_NAME_KEY
    context['GITHUB_TEAM_KEY'] = GITHUB_TEAM_KEY
    return render(request, 'resource_management/github_managemet.html', context)


def add_non_officer_to_github_team(request):
    """takes in the specified user and team from the user and attempts to give them the request github team
    membership

    """
    logger.info(f"[resource_management/github_views.py add_non_officer_to_github_team()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:  # if the user accessing the page is not authorized to access it
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    github = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
    if github.connection_successful:
        post_dict = parser.parse(request.POST.urlencode())
        if there_are_multiple_entries(post_dict, GITHUB_USERNAME_KEY):

            number_of_entries = len(post_dict[GITHUB_USERNAME_KEY])
            logger.info(
                f"[resource_management/github_views.py add_non_officer_to_github_team()] "
                f"{number_of_entries} multiple "
                f"entries detected"
            )
            for index in range(number_of_entries):
                team_name = post_dict[GITHUB_TEAM_KEY][index]
                user_name = post_dict[GITHUB_USERNAME_KEY][index]
                name = post_dict[LEGAL_NAME_KEY][index]
                logger.info(f"[resource_management/github_views.py add_non_officer_to_github_team()] "
                            f"adding user \"{name}\" with github username \"{user_name}\" to team \"{team_name}\"")
                success, message = github.add_non_officer_to_a_team([user_name], team_name)
                if success:
                    NonOfficerGithubMember(
                        team_name=team_name,
                        username=user_name,
                        legal_name=name
                    ).save()
                else:
                    if ERROR_MESSAGE_KEY in request.session:
                        request.session[ERROR_MESSAGE_KEY] += '{}<br>'.format(message)
                    else:
                        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(message)
        else:
            logger.info(
                "[resource_management/github_views.py add_non_officer_to_github_team()] "
                f"only one user detected: {post_dict[GITHUB_USERNAME_KEY]}"
            )
            team_name = post_dict[GITHUB_TEAM_KEY]
            user_name = post_dict[GITHUB_USERNAME_KEY]
            name = post_dict[LEGAL_NAME_KEY]
            logger.info(f"[resource_management/github_views.py add_non_officer_to_github_team()] "
                        f"adding user \"{name}\" with github username \"{user_name}\" to team \"{team_name}\"")

            success, message = github.add_non_officer_to_a_team([user_name], team_name)
            if success:
                NonOfficerGithubMember(
                    team_name=team_name,
                    username=user_name,
                    legal_name=name
                ).save()
            else:
                if ERROR_MESSAGE_KEY in request.session:
                    request.session[ERROR_MESSAGE_KEY] += '{}<br>'.format(message)
                else:
                    request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(message)
    return HttpResponseRedirect(f'{settings.URL_ROOT}resource_management/github')


def update_github_non_officer(request):
    """updates the specified github team membership, either changes the username or the team name that is associated
    with the membership

    """
    logger.info(f"[resource_management/github_views.py update_github_non_officer()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:  # if the user accessing the page is not authorized to access it
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    github = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
    if github.connection_successful:
        if 'action' in request.POST:
            if request.POST['action'] == 'update':
                logger.info("[resource_management/github_views.py update_github_non_officer()] processing an update")
                github_user = NonOfficerGithubMember.objects.get(id=request.POST[GITHUB_RECORD_KEY])
                if github_user.username != request.POST[GITHUB_USERNAME_KEY] \
                        and github_user.team_name != request.POST[GITHUB_TEAM_KEY]:
                    logger.info(
                        f"[resource_management/github_views.py update_github_non_officer()] ll the fields for user"
                        f" {github_user.username} with access to team {github_user.team_name} are different."
                    )
                    github.remove_users_from_a_team([github_user.username], github_user.team_name)
                    success, message = github.add_non_officer_to_a_team([request.POST[GITHUB_USERNAME_KEY]],
                                                                        request.POST[GITHUB_TEAM_KEY])
                if github_user.team_name != request.POST[GITHUB_TEAM_KEY]:
                    logger.info(
                        f"[resource_management/github_views.py update_github_non_officer()] team for user"
                        f" {github_user.username} has been changed from {github_user.team_name} to "
                        f"{request.POST[GITHUB_TEAM_KEY]}."
                    )
                    github.remove_users_from_a_team([github_user.username], github_user.team_name)
                    success, message = github.add_non_officer_to_a_team([github_user.username],
                                                                        request.POST[GITHUB_TEAM_KEY])
                if github_user.username != request.POST[GITHUB_USERNAME_KEY]:
                    logger.info(
                        "[resource_management/github_views.py update_github_non_officer()] team for user"
                        f" {github_user.username} with permission to {github_user.team_name} has been "
                        f"changed to {request.POST[GITHUB_USERNAME_KEY]}."
                    )
                    github.remove_users_from_a_team([github_user.username], github_user.team_name)
                    success, message = github.add_non_officer_to_a_team([request.POST[GITHUB_USERNAME_KEY]],
                                                                        github_user.team_name)
                if success:
                    github_user.team_name = request.POST[GITHUB_TEAM_KEY]
                    github_user.username = request.POST[GITHUB_USERNAME_KEY]
                    github_user.legal_name = request.POST[LEGAL_NAME_KEY]
                    github_user.save()
                else:
                    if ERROR_MESSAGE_KEY in request.session:
                        request.session[ERROR_MESSAGE_KEY] += '{}<br>'.format(message)
                    else:
                        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(message)
            elif request.POST['action'] == 'delete':
                github_user = NonOfficerGithubMember.objects.get(id=request.POST[GITHUB_RECORD_KEY])
                logger.info(
                    "[resource_management/github_views.py update_github_non_officer()] "
                    f"removing {github_user.username}'s access to {github_user.team_name}"
                )
                github.remove_users_from_a_team([github_user.username], github_user.team_name)
                github_user.delete()
    return HttpResponseRedirect(f'{settings.URL_ROOT}resource_management/github')


def create_github_perms():
    """
    Example of users_to_grant_permission_to_github_officers_team
    {
        "githubUsername1" : [
            "team_1", "team_2", "team_3"
        ],
        "githubUsername2" : [
            "team_4", "team_5", "team_6"
        ],
        "githubUsername3" : [
            "team_7", "team_8", "team_9"
        ],
    }
    """
    current_date = datetime.datetime.now()
    term_active = (current_date.year * 10)
    if int(current_date.month) <= 4:
        term_active += 1
    elif int(current_date.month) <= 8:
        term_active += 2
    else:
        term_active += 3
    officers = []

    for index in range(0, 5):
        term = Term.objects.get(term_number=term_active)
        logger.info(
            "[resource_management/github_views.py create_github_perms()] collecting the list of officers"
            f" for the term with term_number {term_active}"
        )
        naughty_officers = NaughtyOfficer.objects.all()
        current_officers = [
            officer for officer in Officer.objects.all().filter(elected_term=term)
            if officer.name not in [name.strip() for name in naughty_officers.name]
        ]

        logger.info(
            f"[resource_management/github_views.py create_github_perms()] officers retrieved = {current_officers}"
        )
        officers.extend(current_officers)
        if (term_active % 10) == 3:
            term_active -= 1
        elif (term_active % 10) == 2:
            term_active -= 1
        elif (term_active % 10) == 1:
            term_active -= 8
    list_of_already_existing_github_team_membership_for_current_officers = []
    for github_membership_for_officer in officers:
        list_of_already_existing_github_team_membership_for_current_officers.extend(
            OfficerGithubTeam.objects.filter(
                officer=github_membership_for_officer,
            )
        )
    users_to_grant_permission_to_github_officers_team = {}

    for github_membership_for_officer in list_of_already_existing_github_team_membership_for_current_officers:
        if github_membership_for_officer.officer.github_username != "":
            if github_membership_for_officer.officer.github_username not in \
                    users_to_grant_permission_to_github_officers_team.keys():
                users_to_grant_permission_to_github_officers_team[
                    github_membership_for_officer.officer.github_username] = [github_membership_for_officer.team_name]
            else:
                users_to_grant_permission_to_github_officers_team[
                    github_membership_for_officer.officer.github_username].append(
                    github_membership_for_officer.team_name)

    non_officer_users_with_access = NonOfficerGithubMember.objects.all()
    logger.info(
        "[resource_management/github_views.py create_github_perms()] non_officer_users_with_access"
        f" = {non_officer_users_with_access}"
    )
    for github_membership_for_non_officer in non_officer_users_with_access:
        if github_membership_for_non_officer.username != "":
            if github_membership_for_non_officer.username not in \
                    users_to_grant_permission_to_github_officers_team.keys():
                users_to_grant_permission_to_github_officers_team[github_membership_for_non_officer.username] = [
                    github_membership_for_non_officer.team_name]
            else:
                users_to_grant_permission_to_github_officers_team[github_membership_for_non_officer.username].append(
                    github_membership_for_non_officer.team_name)
    return users_to_grant_permission_to_github_officers_team
