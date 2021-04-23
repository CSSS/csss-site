import datetime
import logging

from django.shortcuts import render

from administration.Constants import AdminConstants
from csss.views_helper import create_main_context
from elections.models import Election, NomineePosition
from elections.views.Constants_v2 import TAB_STRING, INPUT_ELECTION_ID__VALUE, ELECTION_MANAGEMENT_PERMISSION, \
    BUTTON_MODIFY_ELECTION_ID__NAME, INPUT_ELECTION_ID__NAME, ELECTION_ID, ELECTION__HTML_NAME, NOMINEES_HTML__NAME

logger = logging.getLogger('csss_site')


def get_nominees(request, slug):
    context = create_main_context(request, TAB_STRING)
    election_to_display = Election.objects.get(slug=slug)
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
            if nominee.nominee_speech.nominee.linked_in != "NONE":
                if barrier_needed:
                    nominee.social_media += " | "
                else:
                    nominee.social_media = ""
                nominee.social_media += f'<a href="{nominee.nominee_speech.nominee.linked_in}" ' \
                                        f'target="_blank">LinkedIn Profile</a>'
                barrier_needed = True
            if nominee.nominee_speech.nominee.email != "NONE":
                if barrier_needed:
                    nominee.social_media += " | "
                else:
                    nominee.social_media = ""
                nominee.social_media += f'Email: mailto:{nominee.nominee_speech.nominee.email}'
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


def user_has_election_management_privilege(request):
    return AdminConstants.ELECTION_MANAGEMENT_GROUP_NAME in list(request.user.groups.values_list('name', flat=True))
