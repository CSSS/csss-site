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
            'speech' : 'NomineeSpeech1',
            'social_media' : "Social Media String"
        ],

    }
    """
    speeches = NomineeSpeech.objects.all().filter(
        nominee__nomineelink__id=nominee_link_id
    ).order_by('nomineeposition__position_index')
    speeches_saved = []
    return list(
        {
            speech.id: speech for speech in speeches
            if speech.id not in speeches_saved and append_item(speeches_saved, speech.id)
        }.values()
    )


def append_item(speeches_saved, speech_id):
    speeches_saved.append(speech_id)
    return True
