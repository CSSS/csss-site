from elections.models import NomineeSpeech
from elections.views.Constants import SAVED_NOMINEE_SPEECHES__HTML_NAME


def create_context_for_view_saved_nominee_info_html(context, nominee_obj=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/nominee_links/create_or_update_nominee/view_saved_nominee_info.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the view_saved_nominee_info.html
    nominee_obj -- the nominee obj for the nominee whose speeches have to be shown
    """
    context[SAVED_NOMINEE_SPEECHES__HTML_NAME] = list(
        {
            speech_obj.id: speech_obj
            for speech_obj in NomineeSpeech.objects.all().filter(
                nominee=nominee_obj
            ).order_by('nomineeposition__position_index')
        }.values()
    )
    # this is done to ensure that the speeches are stored in descending order by the
    # high position index assigned to them
