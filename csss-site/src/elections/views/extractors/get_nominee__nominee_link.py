import logging

import markdown

from elections.models import NomineeSpeech

logger = logging.getLogger('csss_site')


def get_election_nominees(nominee_link_id):
    """
    Get the nominee attached to the specified nominee_link

    Keyword Argument
    nominee_link_id -- the id for the nominee_link whose nominee is needed

    Return
    nominees_dict_to_display -- the list of speeches and positions that the linked nominee has in the following format
    {
        [
            'nominee' : 'Nominee'
            'speech' : 'NomineeSpeech',
            'social_media' : "Social Media String"
        ]
    }
    """
    speeches = NomineeSpeech.objects.all().filter(
        nominee__nomineelink__id=nominee_link_id
    ).order_by('nomineeposition__position_index')
    nominees_display_order = {}
    for nominee_speech in speeches:
        if nominee_speech.id not in nominees_display_order:
            nominee_speech.social_media = None
            barrier_needed = False
            if nominee_speech.nominee.facebook != "NONE":
                nominee_speech.social_media = f'<a href="{nominee_speech.nominee.facebook}" ' \
                                              f'target="_blank">Facebook Profile</a>'
                barrier_needed = True
            if nominee_speech.nominee.linkedin != "NONE":
                if barrier_needed:
                    nominee_speech.social_media += " | "
                else:
                    nominee_speech.social_media = ""
                nominee_speech.social_media += f'<a href="{nominee_speech.nominee.linkedin}" ' \
                                               f'target="_blank">LinkedIn Profile</a>'
                barrier_needed = True
            if nominee_speech.nominee.email != "NONE":
                if barrier_needed:
                    nominee_speech.social_media += " | "
                else:
                    nominee_speech.social_media = ""
                nominee_speech.social_media += f'Email: <a href="mailto:{nominee_speech.nominee.email}">' \
                                               f' {nominee_speech.nominee.email}</a>'
                barrier_needed = True
            if nominee_speech.nominee.discord != "NONE":
                if barrier_needed:
                    nominee_speech.social_media += " | "
                else:
                    nominee_speech.social_media = ""
                nominee_speech.social_media += f'Discord Username: {nominee_speech.nominee.discord}'
                nominee_speech.speech = markdown.markdown(
                    nominee_speech.speech, extensions=['sane_lists', 'markdown_link_attr_modifier'],
                    extension_configs={
                        'markdown_link_attr_modifier': {
                            'new_tab': 'on',
                        },
                    }
                )
            nominee_speech.position_names = ", ".join(
                [
                    position.position_name for position in nominee_speech.nomineeposition_set.all()
                ]
            )
            nominees_display_order[nominee_speech.id] = nominee_speech
    return list(nominees_display_order.values())
