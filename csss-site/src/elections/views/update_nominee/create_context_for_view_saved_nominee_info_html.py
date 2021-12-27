from elections.models import NomineeSpeech
from elections.views.Constants import SAVED_NOMINEE_SPEECHES__HTML_NAME


def create_context_for_view_saved_nominee_info_html(context, nominee_obj=None):
    context[SAVED_NOMINEE_SPEECHES__HTML_NAME] = list(
        {
            speech_obj.id: speech_obj
            for speech_obj in NomineeSpeech.objects.all().filter(
                nominee=nominee_obj
            ).order_by('nomineeposition__position_index')
        }.values()
    )
