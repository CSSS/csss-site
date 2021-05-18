import datetime
import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render

from administration.views import user_has_election_management_privilege
from csss.views_helper import create_main_context, ERROR_MESSAGE_KEY
from elections.models import Election, NomineePosition
from elections.views.Constants import TAB_STRING, INPUT_ELECTION_ID__VALUE, ELECTION_MANAGEMENT_PERMISSION, \
    BUTTON_MODIFY_ELECTION_ID__NAME, INPUT_ELECTION_ID__NAME, ELECTION_ID, ELECTION__HTML_NAME, NOMINEES_HTML__NAME
from elections.views.validators.validate_election_slug import validate_election_slug

logger = logging.getLogger('csss_site')


def get_nominees(request, slug):
    context = create_main_context(request, TAB_STRING)
    if not validate_election_slug(slug):
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(
            "Specified slug seems to have more than one election attached to it."
        )
        return HttpResponseRedirect('/error')
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
            context.update(
                {
                    INPUT_ELECTION_ID__VALUE: election_to_display.id,
                    ELECTION_MANAGEMENT_PERMISSION: True,
                    BUTTON_MODIFY_ELECTION_ID__NAME: ELECTION_ID,
                    INPUT_ELECTION_ID__NAME: ELECTION_ID
                }
            )
        logger.info("[elections/election_page.py get_nominees()] time to vote")
        positions = NomineePosition.objects.all().filter(
            nominee_speech__nominee__election__slug=slug,
        ).order_by('position_index')
        nominees_display_order = []
        for nominee in positions:
            nominee.social_media = None
            barrier_needed = False
            if nominee.nominee_speech.nominee.facebook != "NONE":
                nominee.social_media = f'<a href="{nominee.nominee_speech.nominee.facebook}" ' \
                                       f'target="_blank">Facebook Profile</a>'
                barrier_needed = True
            if nominee.nominee_speech.nominee.linkedin != "NONE":
                if barrier_needed:
                    nominee.social_media += " | "
                else:
                    nominee.social_media = ""
                nominee.social_media += f'<a href="{nominee.nominee_speech.nominee.linkedin}" ' \
                                        f'target="_blank">LinkedIn Profile</a>'
                barrier_needed = True
            if nominee.nominee_speech.nominee.email != "NONE":
                if barrier_needed:
                    nominee.social_media += " | "
                else:
                    nominee.social_media = ""
                nominee.social_media += f'Email: <a href="mailto:{nominee.nominee_speech.nominee.email}">' \
                                        f' {nominee.nominee_speech.nominee.email}</a>'
                barrier_needed = True
            if nominee.nominee_speech.nominee.discord != "NONE":
                if barrier_needed:
                    nominee.social_media += " | "
                else:
                    nominee.social_media = ""
                nominee.social_media += f'Discord Username: {nominee.nominee_speech.nominee.discord}'
            nominees_display_order.append(nominee)
        context.update({
            ELECTION__HTML_NAME: election_to_display,
            NOMINEES_HTML__NAME: nominees_display_order,
        })
        return render(request, 'elections/election_page.html', context)
    else:
        logger.info("[elections/election_page.py get_nominees()] cant vote yet")
        return render(request, 'elections/election_page.html', context)
