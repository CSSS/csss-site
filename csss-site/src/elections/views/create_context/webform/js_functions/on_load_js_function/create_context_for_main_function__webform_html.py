from elections.models import Nominee
from elections.views.Constants import NOMINEE_DIV__NAME, NOMINEES_HTML__NAME, ID_KEY, \
    DRAFT_OR_FINALIZED_NOMINEE_TO_DISPLAY__HTML_NAME, NA_STRING
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEES, ELECTION_JSON_KEY__NOM_NAME, \
    ELECTION_JSON_KEY__NOM_FACEBOOK, ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOM_EMAIL, \
    ELECTION_JSON_KEY__NOM_INSTAGRAM, ELECTION_JSON_KEY__NOM_DISCORD_ID, \
    ELECTION_JSON_KEY__NOM_SFUID
from elections.views.create_context.webform.js_functions.create_context_for_add_blank_nominee_html import \
    create_context_for_add_blank_nominee_html
from elections.views.create_context.webform_format.js_functions.on_load_js_function. \
    create_context_for_display_nominee_info_html import \
    create_context_for_display_nominee_info_html


def create_context_for_main_function__webform_html(
    context, nominees_info=None, include_id_for_nominee=False, webform_election=True,
    new_webform_election=True, draft_or_finalized_nominee_to_display=False, election=None,
    get_existing_election_webform=False,
    create_or_update_webform_election=False
):
    """
    populates the context dictionary that is used by
     elections/templates/elections/webform/js_functions/on_load_js_function/main_function.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the main_function.html
    nominees_info -- the list of nominee infos that the user inputted, otherwise None
    include_id_for_nominee -- bool to indicate if the html page has to show the ID for any of the nominees.
     Happens with saved elections
    webform_election -- bool to indicate if the election is a webform election
    new_webform_election -- bool to indicate if the election is a new webform election
    draft_or_finalized_nominee_to_display -- bool to indicate if there is any nominee to show,
     either as a draft or saved
    election -- the election object that is needed for displaying the selected election's nominees
    get_existing_election_webform -- boolean indicator of when the context is being creating for the page
     that shows a saved election
    create_or_update_webform_election -- boolean indicator when the user is trying to create or update an election
    """
    context.update({
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEES
    })
    if get_existing_election_webform:
        #  GET /elections/<slug>/election_modification_webform/
        context[NOMINEES_HTML__NAME] = []
        if election is not None:
            nominees_obj = [
                nominee for nominee in Nominee.objects.all().filter(
                    election=election
                ).order_by('nomineespeech__nomineeposition__position_index',
                           'id')
            ]
            nominee_info_to_add_to_context = {}
            nominee_names = []
            speech_ids = []
            for nominee_obj in nominees_obj:
                if nominee_obj.full_name not in nominee_names:
                    nominee_names.append(nominee_obj.full_name)
                    if nominee_obj.full_name not in nominee_info_to_add_to_context:
                        nominee_info_to_add_to_context[nominee_obj.full_name] = {
                            ID_KEY: nominee_obj.id,
                            ELECTION_JSON_KEY__NOM_NAME: nominee_obj.get_full_name,
                            ELECTION_JSON_KEY__NOM_SFUID: nominee_obj.get_sfuid,
                            ELECTION_JSON_KEY__NOM_FACEBOOK: nominee_obj.get_facebook,
                            ELECTION_JSON_KEY__NOM_INSTAGRAM: nominee_obj.get_instagram,
                            ELECTION_JSON_KEY__NOM_LINKEDIN: nominee_obj.get_linkedin,
                            ELECTION_JSON_KEY__NOM_EMAIL: nominee_obj.get_email,
                            ELECTION_JSON_KEY__NOM_DISCORD_ID: nominee_obj.get_discord_id
                        }
                        create_context_for_display_nominee_info_html(
                            context, draft_or_finalized_nominee_to_display=draft_or_finalized_nominee_to_display,
                            include_id_for_nominee=include_id_for_nominee, webform_election=webform_election,
                            new_webform_election=new_webform_election,
                            nominee_info_to_add_to_context=nominee_info_to_add_to_context,
                            nominee_obj=nominee_obj, speech_ids=speech_ids,
                            populate_nominee_info=True, get_existing_election_webform=get_existing_election_webform
                        )
            context[NOMINEES_HTML__NAME] = [nominee_info for nominee_info in nominee_info_to_add_to_context.values()]
    elif create_or_update_webform_election:
        # POST /elections/new_election_webform
        # POST /elections/<slug>/election_modification_webform/
        context[NOMINEES_HTML__NAME] = []
        if nominees_info is not None and type(nominees_info) is list:
            for nominee_info in nominees_info:  # for the webform pages
                nominee_info_to_add_to_context = {
                    ELECTION_JSON_KEY__NOM_NAME: nominee_info.get(ELECTION_JSON_KEY__NOM_NAME, NA_STRING),
                    ELECTION_JSON_KEY__NOM_SFUID: nominee_info.get(ELECTION_JSON_KEY__NOM_SFUID, NA_STRING),
                    ELECTION_JSON_KEY__NOM_FACEBOOK: nominee_info.get(ELECTION_JSON_KEY__NOM_FACEBOOK, NA_STRING),
                    ELECTION_JSON_KEY__NOM_INSTAGRAM: nominee_info.get(ELECTION_JSON_KEY__NOM_INSTAGRAM, NA_STRING),
                    ELECTION_JSON_KEY__NOM_LINKEDIN: nominee_info.get(ELECTION_JSON_KEY__NOM_LINKEDIN, NA_STRING),
                    ELECTION_JSON_KEY__NOM_EMAIL: nominee_info.get(ELECTION_JSON_KEY__NOM_EMAIL, NA_STRING),
                    ELECTION_JSON_KEY__NOM_DISCORD_ID: nominee_info.get(ELECTION_JSON_KEY__NOM_DISCORD_ID, NA_STRING)
                }
                if ID_KEY in nominee_info:
                    nominee_info_to_add_to_context[ID_KEY] = nominee_info[ID_KEY]
                    include_id_for_nominee = True
                create_context_for_display_nominee_info_html(
                    context, draft_or_finalized_nominee_to_display=draft_or_finalized_nominee_to_display,
                    include_id_for_nominee=include_id_for_nominee, webform_election=webform_election,
                    new_webform_election=new_webform_election,
                    nominee_info_to_add_to_context=nominee_info_to_add_to_context,
                    nominee_info=nominee_info,
                    create_or_update_webform_election=create_or_update_webform_election,
                    populate_nominee_info=True
                )
                context[NOMINEES_HTML__NAME].append(nominee_info_to_add_to_context)
    else:
        # GET request on /elections/new_election_webform
        create_context_for_add_blank_nominee_html(
            context, webform_election=webform_election, new_webform_election=new_webform_election,
            include_id_for_nominee=include_id_for_nominee,
            draft_or_finalized_nominee_to_display=draft_or_finalized_nominee_to_display
        )
    context[DRAFT_OR_FINALIZED_NOMINEE_TO_DISPLAY__HTML_NAME] = 'true'
    if NOMINEES_HTML__NAME not in context or len(context[NOMINEES_HTML__NAME]) == 0:
        context[DRAFT_OR_FINALIZED_NOMINEE_TO_DISPLAY__HTML_NAME] = 'false'
