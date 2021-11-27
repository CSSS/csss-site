from elections.views.Constants import CREATE_OR_UPDATE_VIA_NOMINEE_LINK__HTML_NAME, NOMINEE_DIV__NAME, \
    INPUT_NOMINEE_NAME__NAME, INPUT_NOMINEE_FACEBOOK__NAME, INPUT_NOMINEE_EMAIL__NAME, INPUT_NOMINEE_DISCORD__NAME, \
    INPUT_NOMINEE_ID__NAME, ID_KEY, CREATE_NEW_ELECTION__HTML_NAME, INPUT_NOMINEE_LINKEDIN__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEE, ELECTION_JSON_KEY__NOM_NAME, \
    ELECTION_JSON_KEY__NOM_FACEBOOK, ELECTION_JSON_KEY__NOM_EMAIL, ELECTION_JSON_KEY__NOM_DISCORD, \
    ELECTION_JSON_KEY__NOM_LINKEDIN
from elections.views.create_context.webform_format.js_functions.on_load_js_function.position_names_and_speech_pairings.create_context_for_new_election_html import \
    create_context_for_new_election_html
from elections.views.create_context.webform_format.js_functions.on_load_js_function.position_names_and_speech_pairings.existing_election.create_context_for_draft_nominee_pairings_html import \
    create_context_for_draft_nominee_pairings_html
from elections.views.create_context.webform_format.js_functions.on_load_js_function.position_names_and_speech_pairings.existing_election.create_context_for_nominee_pairings_html import \
    create_context_for_nominee_pairings_html


def create_context_for_display_nominee_info_html(
        context, nominee_obj=None, nominee_info=None, include_id_for_nominee=True, create_new_election=None):
    context.update({
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
        INPUT_NOMINEE_NAME__NAME: ELECTION_JSON_KEY__NOM_NAME,
        INPUT_NOMINEE_FACEBOOK__NAME: ELECTION_JSON_KEY__NOM_FACEBOOK,
        INPUT_NOMINEE_LINKEDIN__NAME: ELECTION_JSON_KEY__NOM_LINKEDIN,
        INPUT_NOMINEE_EMAIL__NAME: ELECTION_JSON_KEY__NOM_EMAIL,
        INPUT_NOMINEE_DISCORD__NAME: ELECTION_JSON_KEY__NOM_DISCORD,

        CREATE_NEW_ELECTION__HTML_NAME: create_new_election,
        CREATE_OR_UPDATE_VIA_NOMINEE_LINK__HTML_NAME: include_id_for_nominee,
        INPUT_NOMINEE_ID__NAME: ID_KEY,
    })
    create_context_for_new_election_html(context, nominee_obj=nominee_obj, nominee_info=nominee_info)
    create_context_for_draft_nominee_pairings_html(context, nominee_info=nominee_info)
    create_context_for_nominee_pairings_html(context, nominee_obj=nominee_obj)
