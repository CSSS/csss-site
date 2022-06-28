import logging

from django.shortcuts import render

from about.models import NewOfficer, Officer
from about.views.create_context.enter_officer_info.create_context_for_enter_officer_info_html import \
    create_context_for_enter_officer_info_html
from about.views.input_new_officers.enter_officer_info.process_specified_new_officer_info import \
    process_specified_new_officer_info
from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from csss.views.context_creation.create_authenticated_contexts import create_context_for_officer_creation_links
from csss.views.context_creation.create_main_context import create_main_context
from csss.views.login import CAS_GROUP_NAME

from django.contrib.auth.models import Group

from csss.views.views import ERROR_MESSAGES_KEY

logger = logging.getLogger('csss_site')


def enter_officer_info(request):
    """
    Shows the page where the user can select the year, term and positions for whom to create the generation links
    http://127.0.0.1:8000/login?next=/about/enter_info
    """
    context = create_main_context(request, tab=TAB_STRING)
    logger.info(f"[about/enter_officer_info.py enter_officer_info()] "
                f"request.POST={request.POST}")
    groups = Group.objects.all().filter(name=CAS_GROUP_NAME)
    new_officers = NewOfficer.objects.all()
    if len(groups) == 1:
        usernames_for_users_from_cas = [user.username for user in groups[0].user_set.all()]
        if request.user.username not in usernames_for_users_from_cas:
            context[ERROR_MESSAGES_KEY] = ["Logged in with a user that is not a verified SFU student"]
            context['not_affiliated_user'] = True
            return render(request, 'about/input_new_officers/enter_officer_info.html', context)
        if len(new_officers.filter(sfu_computing_id=request.user.username)) != 1:
            context[ERROR_MESSAGES_KEY] = [
                f"It does not look like user {request.user.username} has an officer slot open for them"
            ]
            context['not_affiliated_user'] = True
            return render(request, 'about/input_new_officers/enter_officer_info.html', context)
    else:
        context[ERROR_MESSAGES_KEY] = [f"Could not find User Groups {CAS_GROUP_NAME}"]
        return render(request, 'about/input_new_officers/enter_officer_info.html', context)
    process_election = request.method == 'POST'
    new_officer = new_officers.get(sfu_computing_id=request.user.username)
    matching_officer = Officer.objects.all().filter(
        sfuid=request.user.username, position_name=new_officer.position_name
    ).order_by('-elected_term').first()
    if process_election:
        return process_specified_new_officer_info(request, context, new_officer=new_officer)
    create_context_for_enter_officer_info_html(
        request, context, new_officer_obj=new_officer, officer_from_previous_term=matching_officer
    )
    return render(request, 'about/input_new_officers/enter_officer_info.html', context)
