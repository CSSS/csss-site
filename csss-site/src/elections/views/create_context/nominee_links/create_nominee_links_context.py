import datetime
import logging

from about.models import OfficerEmailListAndPositionMapping
from csss.views_helper import ERROR_MESSAGES_KEY
from elections.models import Election, NomineeLink, NomineePosition
from elections.views.Constants import INPUT_DATE__NAME, ELECTION_JSON_KEY__DATE, INPUT_DATE__VALUE, DATE_FORMAT, \
    INPUT_TIME__NAME, ELECTION_JSON_WEBFORM_KEY__TIME, INPUT_TIME__VALUE, TIME_FORMAT, SELECT_ELECTION_TYPE__NAME, \
    ELECTION_JSON_KEY__ELECTION_TYPE, CURRENT_ELECTION_TYPES, SELECTED_ELECTION_TYPE__HTML_NAME, \
    CURRENT_WEBSURVEY_LINK, INPUT_WEBSURVEY__NAME, ELECTION_JSON_KEY__WEBSURVEY, INPUT_REDIRECT_ELECTION__NAME, \
    CREATE_NEW_ELECTION__NAME, \
    UPDATE_EXISTING_ELECTION__NAME, INPUT_REDIRECT_ELECTION_SUBMIT__VALUE, SAVE_ELECTION__VALUE, \
    INPUT_REDIRECT_ELECTION_SUBMIT_AND_CONTINUE_EDITING__VALUE, SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE, \
    NOMINEE_NAMES__HTML_NAME, NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS, NOMINEE_NAMES__VALUE, CURRENT_ELECTION, \
    DRAFT_NOMINEE_LINKS, SAVED_NOMINEE_LINKS__HTML_NAME, SAVED_NOMINEE_LINKS, DELETE__HTML_NAME, DELETE, \
    SAVED_NOMINEE_LINK__ID__HTML_NAME, SAVED_NOMINEE_LINK__ID, SAVED_NOMINEE_LINK__NAME__HTML_NAME, \
    SAVED_NOMINEE_LINK__NAME, SAVED_NOMINEE_LINK__NOMINEE__HTML_NAME, SAVED_NOMINEE_LINK__NOMINEE, \
    NO_NOMINEE_LINKED__HTML_NAME, NOMINEE_LINK_ID__HTML_NAME, NOMINEE_LINK_ID, NO_NOMINEE_LINKED, NOMINEE_LINKS, \
    CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINKS__HTML_NAME, ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK, \
    REQUIRE_NOMINEE_NAMES, TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME, TOGGLE_NOMINEE_LINKS_TO_DELETE, \
    SAVE_NEW_NOMINEE__BUTTON_ID, SAVE_NEW_NOMINEE__BUTTON_ID_VALUE, INPUT_REDIRECT_NOMINEE__NAME, \
    CREATE_OR_UPDATE_NOMINEE__NAME, INPUT_REDIRECT_NOMINEE_SUBMIT__VALUE, SAVE_OR_UPDATE_NOMINEE__VALUE, \
    CREATE_NEW_NOMINEE__HTML_NAME, INPUT_NOMINEE_LINK_ID__NAME, INPUT_NOMINEE_LINK_ID__VALUE, NOMINEE_DIV__NAME, \
    ELECTION_JSON_KEY__NOMINEE, INPUT_NOMINEE_NAME__NAME, ELECTION_JSON_KEY__NOM_NAME, INPUT_NOMINEE_FACEBOOK__NAME, \
    ELECTION_JSON_KEY__NOM_FACEBOOK, INPUT_NOMINEE_LINKEDIN__NAME, ELECTION_JSON_KEY__NOM_LINKEDIN, \
    INPUT_NOMINEE_EMAIL__NAME, ELECTION_JSON_KEY__NOM_EMAIL, INPUT_NOMINEE_DISCORD__NAME, \
    ELECTION_JSON_KEY__NOM_DISCORD, INPUT_NOMINEE_ID__NAME, ID_KEY, DRAFT_NOMINEE_HTML__NAME, \
    INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME, ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, \
    INPUT_NOMINEE_POSITION_NAMES__NAME, ELECTION_JSON_KEY__NOM_POSITION_NAMES, INPUT_NOMINEE_SPEECH__NAME, \
    ELECTION_JSON_KEY__NOM_SPEECH, CURRENT_OFFICER_POSITIONS, INPUT_SPEECH_ID__NAME, \
    ELECTION_JSON_KEY__NOM_POSITION_NAME, FINAL_NOMINEE_HTML__NAME

logger = logging.getLogger('csss_site')


def create_context_for_create_election_nominee_links_html(context, election_date=None, election_time=None,
                                                          election_type=None, create_new_election=False,
                                                          websurvey_link=None, error_messages=None,
                                                          nominee_names=None):
    _create_context_for_display_errors_html(context, error_messages)
    _create_context_for_election_date_html(context, election_date=election_date)
    _create_context_for_election_time_html(context, election_time=election_time)
    _create_context_for_election_type_html(context, election_type=election_type)
    _create_context_for_election_websurvey_html(context, websurvey_link=websurvey_link)
    _create_context_for_election_nominee_names_html(context, nominee_names=nominee_names)
    _create_context_for_submission_buttons_html(context, create_new_election=create_new_election)
    return context


def _create_context_for_display_errors_html(context, error_messages=None):
    if error_messages is not None:
        context[ERROR_MESSAGES_KEY] = error_messages


def _create_context_for_election_date_html(context, election_date=None):
    context.update({
        INPUT_DATE__NAME: ELECTION_JSON_KEY__DATE,
        INPUT_DATE__VALUE: election_date.strftime(DATE_FORMAT) if type(election_date) is datetime.datetime
        else election_date
    })


def _create_context_for_election_time_html(context, election_time=None):
    context.update({
        INPUT_TIME__NAME: ELECTION_JSON_WEBFORM_KEY__TIME,
        INPUT_TIME__VALUE: election_time.strftime(TIME_FORMAT) if type(election_time) is datetime.datetime
        else election_time
    })


def _create_context_for_election_type_html(context, election_type=None):
    context.update({
        SELECT_ELECTION_TYPE__NAME: ELECTION_JSON_KEY__ELECTION_TYPE,
        CURRENT_ELECTION_TYPES: Election.election_type_choices,
        SELECTED_ELECTION_TYPE__HTML_NAME: election_type
    })


def _create_context_for_election_websurvey_html(context, websurvey_link=None):
    context.update({
        INPUT_WEBSURVEY__NAME: ELECTION_JSON_KEY__WEBSURVEY,
        CURRENT_WEBSURVEY_LINK: websurvey_link,
    })


def _create_context_for_election_nominee_names_html(context, require_nominee_names=True, nominee_names=None):
    context[NOMINEE_NAMES__HTML_NAME] = NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS
    context[REQUIRE_NOMINEE_NAMES] = require_nominee_names
    if nominee_names is not None:
        context[NOMINEE_NAMES__VALUE] = nominee_names


def _create_context_for_submission_buttons_html(context, create_new_election=False):
    context.update({
        INPUT_REDIRECT_ELECTION__NAME: CREATE_NEW_ELECTION__NAME if create_new_election
        else UPDATE_EXISTING_ELECTION__NAME,
        INPUT_REDIRECT_ELECTION_SUBMIT__VALUE: SAVE_ELECTION__VALUE,
        INPUT_REDIRECT_ELECTION_SUBMIT_AND_CONTINUE_EDITING__VALUE: SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE
    })


def create_context_for_update_election_nominee_links_html(
        context, error_messages=None, nominee_links=None, election_date=None, election_time=None, election_type=None,
        websurvey_link=None, create_new_election=False, draft_nominee_links=None,
        new_nominee_names=None, slug=None):
    require_nominee_names = (
            (nominee_links is None or len(nominee_links) == 0) and
            (draft_nominee_links is None or len(draft_nominee_links) == 0)
    )
    _create_context_for_display_errors_html(context, error_messages=error_messages)
    context[CURRENT_ELECTION] = None if slug is None else Election.objects.get(slug=slug)
    _create_context_for_election_date_html(context, election_date=election_date)
    _create_context_for_election_time_html(context, election_time=election_time)
    _create_context_for_election_type_html(context, election_type=election_type)
    _create_context_for_election_websurvey_html(context, websurvey_link=websurvey_link)
    _create_context_for_nominee_links_table_html(context, draft_nominee_links=draft_nominee_links, slug=slug,
                                                 nominee_links=nominee_links)
    _create_context_for_election_nominee_names_html(context, require_nominee_names=require_nominee_names,
                                                    nominee_names=new_nominee_names)
    _create_context_for_submission_buttons_html(context, create_new_election=create_new_election)
    context[TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME] = TOGGLE_NOMINEE_LINKS_TO_DELETE


def _create_context_for_nominee_links_table_html(context, draft_nominee_links=None, slug=None, nominee_links=None):
    _create_context_for_draft_nominee_links_html(context, draft_nominee_links=draft_nominee_links, slug=slug)
    _create_context_for_final_nominee_links_html(context, nominee_links=nominee_links)


def _create_context_for_draft_nominee_links_html(context, draft_nominee_links=None, slug=None):
    if draft_nominee_links is not None:
        context[DRAFT_NOMINEE_LINKS] = draft_nominee_links
    context[SAVED_NOMINEE_LINKS__HTML_NAME] = SAVED_NOMINEE_LINKS
    context[DELETE__HTML_NAME] = DELETE
    context[SAVED_NOMINEE_LINK__ID__HTML_NAME] = SAVED_NOMINEE_LINK__ID
    context[SAVED_NOMINEE_LINK__NAME__HTML_NAME] = SAVED_NOMINEE_LINK__NAME
    context[SAVED_NOMINEE_LINK__NOMINEE__HTML_NAME] = SAVED_NOMINEE_LINK__NOMINEE
    context[NO_NOMINEE_LINKED__HTML_NAME] = NO_NOMINEE_LINKED
    context[TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME] = TOGGLE_NOMINEE_LINKS_TO_DELETE
    context[CURRENT_ELECTION] = None if slug is None else Election.objects.get(slug=slug)
    context[CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINKS__HTML_NAME] = \
        ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK
    context[NOMINEE_LINK_ID__HTML_NAME] = NOMINEE_LINK_ID


def _create_context_for_final_nominee_links_html(context, nominee_links=None):
    context[NOMINEE_LINKS] = nominee_links
    context[SAVED_NOMINEE_LINKS__HTML_NAME] = SAVED_NOMINEE_LINKS
    context[DELETE__HTML_NAME] = DELETE
    context[SAVED_NOMINEE_LINK__ID__HTML_NAME] = SAVED_NOMINEE_LINK__ID
    context[SAVED_NOMINEE_LINK__NAME__HTML_NAME] = SAVED_NOMINEE_LINK__NAME
    context[SAVED_NOMINEE_LINK__NOMINEE__HTML_NAME] = SAVED_NOMINEE_LINK__NOMINEE
    context[NO_NOMINEE_LINKED__HTML_NAME] = NO_NOMINEE_LINKED
    context[TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME] = TOGGLE_NOMINEE_LINKS_TO_DELETE
    context[CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINKS__HTML_NAME] = \
        ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK
    context[NOMINEE_LINK_ID__HTML_NAME] = NOMINEE_LINK_ID

def create_context_for_update_nominee_html(context, nominee_link_id=None, error_messages=None,
                                           nominee_info=None):
    nominee_links = NomineeLink.objects.all().filter(id=nominee_link_id)
    create_new_nominee = not (len(nominee_links) == 1 and nominee_links[0].nominee is not None)
    _create_context_for_display_errors_html(context, error_messages=error_messages)
    _create_context_for_form_html(
        context, create_new_nominee=create_new_nominee, nominee_link_id=nominee_link_id
    )
    _create_context_for_main_function_html(
        context, nominee_link_id=nominee_link_id, create_new_nominee=create_new_nominee, nominee_info=nominee_info
    )
    __create_context_for_add_blank_speech_html(context)
    return context

def _create_context_for_form_html(context, create_new_nominee=None, nominee_link_id=None):
    context.update({
        SAVE_NEW_NOMINEE__BUTTON_ID: SAVE_NEW_NOMINEE__BUTTON_ID_VALUE,
        INPUT_REDIRECT_NOMINEE__NAME: CREATE_OR_UPDATE_NOMINEE__NAME,
        INPUT_REDIRECT_NOMINEE_SUBMIT__VALUE: SAVE_OR_UPDATE_NOMINEE__VALUE,
        CREATE_NEW_NOMINEE__HTML_NAME: create_new_nominee,
        INPUT_NOMINEE_LINK_ID__NAME: NOMINEE_LINK_ID,
        INPUT_NOMINEE_LINK_ID__VALUE: nominee_link_id,
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,

    })

def _create_context_for_main_function_html(context, nominee_link_id=None, create_new_nominee=False, nominee_info=None):
    context.update({
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
        INPUT_NOMINEE_NAME__NAME: ELECTION_JSON_KEY__NOM_NAME,
        INPUT_NOMINEE_FACEBOOK__NAME: ELECTION_JSON_KEY__NOM_FACEBOOK,
        INPUT_NOMINEE_LINKEDIN__NAME: ELECTION_JSON_KEY__NOM_LINKEDIN,
        INPUT_NOMINEE_EMAIL__NAME: ELECTION_JSON_KEY__NOM_EMAIL,
        INPUT_NOMINEE_DISCORD__NAME: ELECTION_JSON_KEY__NOM_DISCORD,
        INPUT_NOMINEE_ID__NAME: ID_KEY,
        CREATE_NEW_NOMINEE__HTML_NAME: create_new_nominee,
    })
    nominee_link = NomineeLink.objects.get(id=nominee_link_id)
    nominee_obj = nominee_link.nominee if nominee_link.nominee is not None else None

    if nominee_info is not None:
        context.update(
            {
                DRAFT_NOMINEE_HTML__NAME: {
                    ID_KEY: None if nominee_obj is None else nominee_obj.id,
                    ELECTION_JSON_KEY__NOM_NAME: nominee_info[ELECTION_JSON_KEY__NOM_NAME],
                    ELECTION_JSON_KEY__NOM_FACEBOOK: nominee_info[ELECTION_JSON_KEY__NOM_FACEBOOK],
                    ELECTION_JSON_KEY__NOM_LINKEDIN: nominee_info[ELECTION_JSON_KEY__NOM_LINKEDIN],
                    ELECTION_JSON_KEY__NOM_EMAIL: nominee_info[ELECTION_JSON_KEY__NOM_EMAIL],
                    ELECTION_JSON_KEY__NOM_DISCORD: nominee_info[ELECTION_JSON_KEY__NOM_DISCORD]
                }
            }
        )
    elif nominee_obj is not None:
        context.update(
            {
                DRAFT_NOMINEE_HTML__NAME: {
                    ID_KEY: None if nominee_obj is None else nominee_obj.id,
                    ELECTION_JSON_KEY__NOM_NAME: nominee_obj.name,
                    ELECTION_JSON_KEY__NOM_FACEBOOK: nominee_obj.facebook,
                    ELECTION_JSON_KEY__NOM_LINKEDIN: nominee_obj.linkedin,
                    ELECTION_JSON_KEY__NOM_EMAIL: nominee_obj.email,
                    ELECTION_JSON_KEY__NOM_DISCORD: nominee_obj.discord
                }
            }
        )
    _create_context_for_new_election_html(context, nominee_info=nominee_info)
    _create_context_for_existing_election_html(context, nominee_info=nominee_info, nominee_obj=nominee_obj)
    _create_context_for_view_nominee_html(context, nominee_link_id=nominee_link_id)

def _create_context_for_new_election_html(context, nominee_info=None):
    context.update({
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
        INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME: ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS,
        INPUT_NOMINEE_POSITION_NAMES__NAME: ELECTION_JSON_KEY__NOM_POSITION_NAMES,
        INPUT_NOMINEE_SPEECH__NAME: ELECTION_JSON_KEY__NOM_SPEECH,
        CURRENT_OFFICER_POSITIONS: [
            position for position in OfficerEmailListAndPositionMapping.objects.all().filter(
                marked_for_deletion=False, elected_via_election_officer=True
            )
        ],
    })
    if nominee_info is not None:
        context[DRAFT_NOMINEE_HTML__NAME][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = \
            nominee_info[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS]

def _create_context_for_existing_election_html(context, nominee_info=None, nominee_obj=None):
    context.update({
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
        INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME: ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS,
        INPUT_NOMINEE_POSITION_NAMES__NAME: ELECTION_JSON_KEY__NOM_POSITION_NAMES,
        INPUT_NOMINEE_SPEECH__NAME: ELECTION_JSON_KEY__NOM_SPEECH,
        INPUT_SPEECH_ID__NAME: ID_KEY,
        CURRENT_OFFICER_POSITIONS: [
            position for position in OfficerEmailListAndPositionMapping.objects.all().filter(
                marked_for_deletion=False, elected_via_election_officer=True
            )
        ],
    })
    if nominee_info is None and nominee_obj is not None:
        positions = NomineePosition.objects.all().filter(
            nominee_speech__nominee_id=nominee_obj.id
        ).order_by('position_index')
        pairings = {}
        for position in positions:
            speech_id = position.nominee_speech.id
            if speech_id in pairings:
                pairings[speech_id][ELECTION_JSON_KEY__NOM_POSITION_NAMES].append({
                    ID_KEY: position.id,
                    ELECTION_JSON_KEY__NOM_POSITION_NAME: position.position_name
                })
            else:
                pairings[speech_id] = {
                    ELECTION_JSON_KEY__NOM_SPEECH: position.nominee_speech.speech,
                    ID_KEY: speech_id,
                    ELECTION_JSON_KEY__NOM_POSITION_NAMES: [{
                        ID_KEY: position.id,
                        ELECTION_JSON_KEY__NOM_POSITION_NAME: position.position_name
                    }]
                }
        if DRAFT_NOMINEE_HTML__NAME not in context:
            context[DRAFT_NOMINEE_HTML__NAME] = {}
        context[DRAFT_NOMINEE_HTML__NAME][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS] = \
            list(pairings.values())

def _create_context_for_view_nominee_html(context, nominee_link_id=None):
    if nominee_link_id is not None:
        context.update({FINAL_NOMINEE_HTML__NAME: get_election_nominees(nominee_link_id)})



def __create_context_for_add_blank_speech_html(context):
    context.update({
        NOMINEE_DIV__NAME: ELECTION_JSON_KEY__NOMINEE,
        INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME: ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS,
        INPUT_NOMINEE_POSITION_NAMES__NAME: ELECTION_JSON_KEY__NOM_POSITION_NAMES,
        INPUT_NOMINEE_SPEECH__NAME: ELECTION_JSON_KEY__NOM_SPEECH,
    })
