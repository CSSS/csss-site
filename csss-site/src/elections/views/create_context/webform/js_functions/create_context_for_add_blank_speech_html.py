from about.models import OfficerEmailListAndPositionMapping
from elections.views.Constants import NOMINEE_DIV__NAME, INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME, \
    INPUT_NOMINEE_POSITION_NAMES__NAME, INPUT_NOMINEE_SPEECH__NAME, CURRENT_OFFICER_POSITIONS
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEES, \
    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, ELECTION_JSON_KEY__NOM_POSITION_NAMES, \
    ELECTION_JSON_KEY__NOM_SPEECH


def create_context_for_add_blank_speech_html(context):
    """
    populates the context dictionary that is used by elections/templates/elections/webform_format/js_functions/add_blank_speech.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the add_blank_speech.html
    """
    context.update({
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEES,
        INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME: ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS,
        INPUT_NOMINEE_POSITION_NAMES__NAME: ELECTION_JSON_KEY__NOM_POSITION_NAMES,
        INPUT_NOMINEE_SPEECH__NAME: ELECTION_JSON_KEY__NOM_SPEECH,
        CURRENT_OFFICER_POSITIONS: [
            position for position in OfficerEmailListAndPositionMapping.objects.all().filter(
                marked_for_deletion=False, elected_via_election_officer=True
            )
        ]
    })
