from elections.models import NomineeSpeech
from elections.views.Constants import NOMINEE_DIV__NAME, \
    INPUT_NOMINEE_NAME__NAME, INPUT_NOMINEE_FACEBOOK__NAME, INPUT_NOMINEE_EMAIL__NAME, INPUT_NOMINEE_DISCORD__NAME, \
    INPUT_NOMINEE_ID__NAME, ID_KEY, INPUT_NOMINEE_LINKEDIN__NAME, \
    INCLUDE_ID_FOR_NOMINEE_IN_WEBFORM__HTML_NAME, ELECTION_MODIFICATION_VIA_WEBFORM__HTML_NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOM_NAME, \
    ELECTION_JSON_KEY__NOM_FACEBOOK, ELECTION_JSON_KEY__NOM_EMAIL, ELECTION_JSON_KEY__NOM_DISCORD, \
    ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOMINEES, ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS
from elections.views.create_context.webform_format.js_functions.on_load_js_function.\
    position_names_and_speech_pairings.create_context_for_position_names_and_speech_pairing_html import \
    create_context_for_position_names_and_speech_pairing_html


def create_context_for_display_nominee_info_html(
        context, draft_or_finalized_nominee_to_display=False, include_id_for_nominee=False,
        webform_election=True, new_webform_election=True,
        nominee_info_to_add_to_context=None, nominee_info=None, nominee_obj=None,
        speech_ids=None, populate_nominee_info=False,
        create_or_update_webform_election=False,
        get_existing_election_webform=False
):
    """
    populates the context dictionary that is used by
     elections/templates/elections/webform_format/display_nominee_info.html

    context -- the context dictionary that has to be populated for the display_nominee_info.html
    draft_or_finalized_nominee_to_display -- no draft nominee from user's input or finalized nominee in DB to show
    include_id_for_nominee -- attaches the ID for a nominee to the webform
    webform_election -- bool to indicate if the election is a webform election
    new_webform_election -- bool to indicate if the election is a new webform election
    nominee_info_to_add_to_context -- the nominee info that is being constructed for current nominee that needs to
     be added to the context dictionary
    nominee_info -- the nominee info that the user inputted, otherwise None
    nominee_obj -- the object that contains the saved nominee info
    speech_ids -- keeps tracks of the speech_ids attached to the context so far
    populate_nominee_info -- flag to indicate whether or not to populate the nominee_info when being called via
     create_context_for_update_election__webform_html context creator
    get_existing_election_webform -- boolean indicator of when the context is being creating for the page
     that shows a saved election
    create_or_update_webform_election -- boolean indicator when the user is trying to create or update an election
    """
    context.update({
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEES,
        INPUT_NOMINEE_NAME__NAME: ELECTION_JSON_KEY__NOM_NAME,
        INPUT_NOMINEE_FACEBOOK__NAME: ELECTION_JSON_KEY__NOM_FACEBOOK,
        INPUT_NOMINEE_LINKEDIN__NAME: ELECTION_JSON_KEY__NOM_LINKEDIN,
        INPUT_NOMINEE_EMAIL__NAME: ELECTION_JSON_KEY__NOM_EMAIL,
        INPUT_NOMINEE_DISCORD__NAME: ELECTION_JSON_KEY__NOM_DISCORD,
    })
    if draft_or_finalized_nominee_to_display:
        context.update({
            INCLUDE_ID_FOR_NOMINEE_IN_WEBFORM__HTML_NAME: include_id_for_nominee,
            INPUT_NOMINEE_ID__NAME: ID_KEY,
            ELECTION_MODIFICATION_VIA_WEBFORM__HTML_NAME: webform_election,
        })
        if webform_election:
            if create_or_update_webform_election:
                # POST /elections/new_election_webform
                # POST /elections/<slug>/election_modification_webform/
                create_context_for_position_names_and_speech_pairing_html(
                    context, nominee_info_to_add_to_context=nominee_info_to_add_to_context,
                    nominee_info=nominee_info, new_election_or_nominee=new_webform_election,
                    populate_nominee_info=populate_nominee_info
                )
            elif get_existing_election_webform:
                # GET /elections/<slug>/election_modification_webform/
                if ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS not in nominee_info_to_add_to_context[nominee_obj.name]:  # noqa: E501
                    nominee_info_to_add_to_context[nominee_obj.name][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = []  # noqa: E501
                speech_objs = NomineeSpeech.objects.all().filter(
                    nominee=nominee_obj
                ).order_by('nomineeposition__position_index')
                for speech_obj in speech_objs:
                    create_context_for_position_names_and_speech_pairing_html(
                        context, nominee_info_to_add_to_context=nominee_info_to_add_to_context,
                        speech_obj=speech_obj, nominee_name=nominee_obj.name,
                        new_election_or_nominee=new_webform_election, speech_ids=speech_ids,
                        populate_nominee_info=populate_nominee_info
                    )
        else:
            if nominee_info is not None:
                # POST /elections/create_or_update_via_nominee_links/?nominee_link_id=2
                create_context_for_position_names_and_speech_pairing_html(
                    context, nominee_info_to_add_to_context=nominee_info_to_add_to_context,
                    nominee_info=nominee_info, populate_nominee_info=True, new_election_or_nominee=nominee_obj is None
                )
            elif nominee_obj is not None:
                # GET /elections/create_or_update_via_nominee_links/?nominee_link_id=2
                nominee_info_to_add_to_context[nominee_obj.name][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = []
                speech_objs = NomineeSpeech.objects.all().filter(
                    nominee=nominee_obj
                ).order_by('nomineeposition__position_index')
                speech_ids = []
                for speech_obj in speech_objs:
                    create_context_for_position_names_and_speech_pairing_html(
                        context, nominee_info_to_add_to_context=nominee_info_to_add_to_context, speech_obj=speech_obj,
                        populate_nominee_info=True, nominee_name=nominee_obj.name, new_election_or_nominee=False,
                        speech_ids=speech_ids
                    )
