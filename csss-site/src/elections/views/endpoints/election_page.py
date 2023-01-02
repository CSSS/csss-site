import logging

from django.conf import settings
from django.shortcuts import render

from csss.views.context_creation.create_election_page_context import create_election_page_context
from csss.views.views import ERROR_MESSAGES_KEY
from csss.views_helper import get_current_date
from elections.models import Election, NomineePosition, NomineeLink
from elections.views.Constants import TAB_STRING, ELECTION__HTML_NAME, \
    NOMINEES_HTML__NAME, PRE_EXISTING_ELECTION, DELETE_EXISTING_NOMINEE_LINKS_MESSAGE, \
    ENDPOINT_DELETE_NOMINEE_LINKS, DELETE_NOMINEE_LINKS_REDIRECT_PATH_KEY
from elections.views.validators.validate_election_slug import validate_election_slug

logger = logging.getLogger('csss_site')


def get_nominees(request, slug):
    context, user_is_election_officer = create_election_page_context(request, TAB_STRING)
    if not validate_election_slug(slug):
        context[ERROR_MESSAGES_KEY] = ["specified slug has an incorrect number of elections attached to it."]
        return render(request, 'elections/election_page.html', context)
    election_to_display = Election.objects.get(slug=slug)
    if user_is_election_officer:
        privilege_message = "user does have election management privilege"
    else:
        privilege_message = "user does not have election management privilege"
    logger.info(f"[elections/election_page.py get_nominees()] determining if election with slug {slug}"
                f"needs to be shown as its date is {election_to_display.date} and the {privilege_message}")
    if election_to_display.date <= get_current_date() or user_is_election_officer:
        if user_is_election_officer:
            nominee_links = NomineeLink.objects.all().exclude(election__slug=slug)
            context[PRE_EXISTING_ELECTION] = False
            if len(nominee_links) > 0:
                context.update({
                    PRE_EXISTING_ELECTION: True,
                    DELETE_EXISTING_NOMINEE_LINKS_MESSAGE: (
                        f'<a href="{ settings.URL_ROOT }elections/{ nominee_links[0].election.slug }'
                        f'/{ENDPOINT_DELETE_NOMINEE_LINKS}?'
                        f'{DELETE_NOMINEE_LINKS_REDIRECT_PATH_KEY}={request.path}"> '
                        'Click here delete the nominee links for the '
                        f'"{nominee_links[0].election.human_friendly_name}'
                        f' election before creating Nominee Links for this election.'
                        '</a>'
                    )
                })
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
