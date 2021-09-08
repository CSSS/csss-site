import datetime
import logging

from django.shortcuts import render

from administration.views import user_has_election_management_privilege
from csss.views.context_creation.create_main_context import create_main_context
from csss.views.views import ERROR_MESSAGES_KEY
from elections.models import Election, NomineePosition, NomineeLink
from elections.views.Constants import TAB_STRING, INPUT_ELECTION_ID__VALUE, ELECTION_MANAGEMENT_PERMISSION, \
    BUTTON_MODIFY_ELECTION_ID__NAME, INPUT_ELECTION_ID__NAME, ELECTION_ID, ELECTION__HTML_NAME, NOMINEES_HTML__NAME, \
    PRE_EXISTING_ELECTION, DELETE_EXISTING_NOMINEE_LINKS_MESSAGE
from elections.views.validators.validate_election_slug import validate_election_slug

logger = logging.getLogger('csss_site')


def get_nominees(request, slug):
    context = create_main_context(request, TAB_STRING)
    if not validate_election_slug(slug):
        context[ERROR_MESSAGES_KEY] = ["Specified slug seems to have more than one election attached to it."]
        return render(request, 'elections/election_page.html', context)
    election_to_display = Election.objects.get(slug=slug)
    election_management_privilege = user_has_election_management_privilege(request)
    if election_management_privilege:
        privilege_message = "user does have election management privilege"
    else:
        privilege_message = "user does not have election management privilege"
    logger.info(f"[elections/election_page.py get_nominees()] determining if election with slug {slug}"
                f"needs to be shown as its date is {election_to_display.date} and the {privilege_message}")
    if election_to_display.date <= datetime.datetime.now() or user_has_election_management_privilege(request):
        if user_has_election_management_privilege(request):
            nominee_links = NomineeLink.objects.all().exclude(election__slug=slug)
            context[PRE_EXISTING_ELECTION] = False
            if len(nominee_links) > 0:
                context.update({
                    PRE_EXISTING_ELECTION: True,
                    DELETE_EXISTING_NOMINEE_LINKS_MESSAGE: (
                        f"Please delete the nominee links for the {nominee_links[0].election.human_friendly_name} "
                        f"election before creating a new election via nominee link"
                    )
                })
            context.update(
                {
                    INPUT_ELECTION_ID__VALUE: election_to_display.id,
                    ELECTION_MANAGEMENT_PERMISSION: True,
                    BUTTON_MODIFY_ELECTION_ID__NAME: ELECTION_ID,
                    INPUT_ELECTION_ID__NAME: ELECTION_ID,

                }
            )
        logger.info("[elections/election_page.py get_nominees()] time to vote")
        positions = NomineePosition.objects.all().filter(
            nominee_speech__nominee__election__slug=slug,
        ).order_by('position_index')
        context.update({
            ELECTION__HTML_NAME: election_to_display,
            NOMINEES_HTML__NAME: positions,
        })
        return render(request, 'elections/election_page.html', context)
    else:
        logger.info("[elections/election_page.py get_nominees()] cant vote yet")
        return render(request, 'elections/election_page.html', context)
