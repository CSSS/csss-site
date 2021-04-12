import datetime
import logging

from django.shortcuts import render

from csss.views_helper import create_main_context
from elections.models import Election, NomineePosition
from elections.views.Constants import TAB_STRING

logger = logging.getLogger('csss_site')


def get_nominees(request, slug):
    context = create_main_context(request, TAB_STRING)
    retrieved_obj = Election.objects.get(slug=slug)
    if retrieved_obj.date <= datetime.datetime.now():
        logger.info("[elections/Constants.py get_nominees()] time to vote")
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
            'election': retrieved_obj,
            'election_date': retrieved_obj.date.strftime("%Y-%m-%d"),
            'nominees': nominees_display_order,
        })
        return render(request, 'elections/nominee_list.html', context)
    else:
        logger.info("[elections/Constants.py get_nominees()] cant vote yet")
        context.update({'nominees': 'none', })
        return render(request, 'elections/nominee_list.html', context)
