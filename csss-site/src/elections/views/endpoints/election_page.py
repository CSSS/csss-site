import datetime
import logging

from django.shortcuts import render

from administration.Constants import AdminConstants
from csss.views_helper import create_main_context
from elections.models import Election, NomineePosition
from elections.views.Constants import TAB_STRING, ELECTION_ID_KEY, DATE_FORMAT, DISPLAY_ELECTION_KEY

logger = logging.getLogger('csss_site')


def get_nominees(request, slug):
    context = create_main_context(request, TAB_STRING)
    election_to_display = Election.objects.get(slug=slug)
    if election_to_display.date <= datetime.datetime.now() or user_has_election_management_privilege(request):
        if user_has_election_management_privilege(request):
            context.update(
                {
                    'election_id_key': ELECTION_ID_KEY,
                    ELECTION_ID_KEY: election_to_display.id
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
            'election': election_to_display,
            'election_date': election_to_display.date.strftime(DATE_FORMAT),
            'nominees': nominees_display_order,
            'display_election_key': DISPLAY_ELECTION_KEY
        })
        return render(request, 'elections/election_page.html', context)
    else:
        logger.info("[elections/election_page.py get_nominees()] cant vote yet")
        context.update({'nominees': 'none', })
        return render(request, 'elections/election_page.html', context)


def user_has_election_management_privilege(request):
    return AdminConstants.ELECTION_MANAGEMENT_GROUP_NAME in list(request.user.groups.values_list('name', flat=True))
