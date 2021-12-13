from elections.views.Constants import NOMINEE_DIV__NAME, \
    INPUT_NOMINEE_NAME__NAME, INPUT_NOMINEE_FACEBOOK__NAME, INPUT_NOMINEE_EMAIL__NAME, INPUT_NOMINEE_DISCORD__NAME, \
    INPUT_NOMINEE_ID__NAME, ID_KEY, INPUT_NOMINEE_LINKEDIN__NAME, \
    INCLUDE_ID_FOR_NOMINEE_IN_WEBFORM__HTML_NAME, ELECTION_MODIFICATION_VIA_WEBFORM__HTML_NAME, \
    NEW_WEBFORM_ELECTION__HTML__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOM_NAME, \
    ELECTION_JSON_KEY__NOM_FACEBOOK, ELECTION_JSON_KEY__NOM_EMAIL, ELECTION_JSON_KEY__NOM_DISCORD, \
    ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOMINEES
from elections.views.create_context.webform_format.js_functions.on_load_js_function.position_names_and_speech_pairings.existing_election.create_context_for_position_names_and_speech_pairing_html import \
    create_context_for_position_names_and_speech_pairing_html


def create_context_for_display_nominee_info_html(
        context, draft_or_finalized_nominee_to_display=False, include_id_for_nominee=False,
        webform_election=True, new_webform_election=True,
        nominee_info_to_add_to_context=None, nominee_info=None
        # nominee_info_to_add_to_context=None
        # nominee_info_for_context=None, nominee_obj=None, nominee_info=None,
        # , speech_ids=None,
        # nominee_info_position_and_speech_pairing=None
):
    """
    nominee_obj -- the nominee obj if there is saved nominee for webform
    nominee_info -- the dict that contains the user input for nominee that hasn't been saved
    include_id_for_nominee -- attaches the ID for a nominee to the webform
    create_new_election -- True if nominee_link election and there is no saved nominees yet
    draft_or_finalized_nominee_to_display -- no draft nominee from user's input or finalized nominee in DB to show
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
            NEW_WEBFORM_ELECTION__HTML__NAME: new_webform_election
        })
        if webform_election:
            if new_webform_election:
                create_context_for_position_names_and_speech_pairing_html(
                    context, nominee_info_to_add_to_context=nominee_info_to_add_to_context,
                    nominee_info=nominee_info,
                )
                # create_context_for_new_election_html(
                #     context, nominee_info_for_context=nominee_info_for_context, nominee_info=nominee_info,
                #     nominee_obj=nominee_obj
                # )
            else:
                pass
                # if ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS not in nominee_info_for_context[
                #     nominee_obj.name]:
                #     nominee_info_for_context[nominee_obj.name][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = []
                # for speech_obj in NomineeSpeech.objects.all().filter(nominee=nominee_obj).order_by(
                #         'nomineeposition__position_index'
                # ):
                #     create_context_for_position_names_and_speech_pairing_html(
                #         context,
                #         speech_obj=speech_obj, speech_ids=speech_ids,
                #         nominee_info_for_context=nominee_info_for_context, nominee_obj=nominee_obj
                #     )

        else:
            pass
            # if nominee_info is not None and ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS in nominee_info:
            #     position_and_speech_pairings = nominee_info[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS]
            #     create_context_for_position_names_and_speech_pairing_html(
            #         context, nominee_info_position_and_speech_pairing=position_and_speech_pairings
            #     )
            #     create_context_for_position_names_and_speech_pairing_html(
            #         context
            #     )
