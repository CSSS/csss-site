import datetime
import logging

from csss.views_helper import ERROR_MESSAGES_KEY
from elections.models import Election
from elections.views.Constants import INPUT_DATE__NAME, ELECTION_JSON_KEY__DATE, INPUT_DATE__VALUE, DATE_FORMAT, \
    INPUT_TIME__NAME, ELECTION_JSON_WEBFORM_KEY__TIME, INPUT_TIME__VALUE, TIME_FORMAT, SELECT_ELECTION_TYPE__NAME, \
    ELECTION_JSON_KEY__ELECTION_TYPE, CURRENT_ELECTION_TYPES, SELECTED_ELECTION_TYPE__HTML_NAME, \
    CURRENT_WEBSURVEY_LINK, INPUT_WEBSURVEY__NAME, ELECTION_JSON_KEY__WEBSURVEY, SAVE_NEW_JSON_ELECTION__BUTTON_ID, \
    SAVE_NEW_JSON_ELECTION__BUTTON_ID_VALUE, INPUT_REDIRECT_ELECTION__NAME, CREATE_NEW_ELECTION__NAME, \
    UPDATE_EXISTING_ELECTION__NAME, INPUT_REDIRECT_ELECTION_SUBMIT__VALUE, SAVE_ELECTION__VALUE, \
    SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID, \
    SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID_VALUE, \
    INPUT_REDIRECT_ELECTION_SUBMIT_AND_CONTINUE_EDITING__VALUE, SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE, \
    NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS__HTML_NAME, NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS

logger = logging.getLogger('csss_site')


def create_context_for_create_election_nominee_links_html(context, election_date=None, election_time=None,
                                                          election_type=None, create_new_election=False,
                                                          websurvey_link=None, error_messages=None):
    _create_context_for_display_errors_html(context, error_messages)
    _create_context_for_election_date_html(context, election_date=election_date)
    _create_context_for_election_time_html(context, election_time=election_time)
    _create_context_for_election_type_html(context, election_type=election_type)
    _create_context_for_election_websurvey_html(context, websurvey_link=websurvey_link)
    _create_context_for_election_nominees_html(context)
    _create_context_for_submission_buttons_html(context, create_new_election=create_new_election)
    return context


def _create_context_for_display_errors_html(context, error_messages=None):
    if error_messages is not None:
        context.update({ERROR_MESSAGES_KEY: error_messages})


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
        CURRENT_WEBSURVEY_LINK: websurvey_link,
        INPUT_WEBSURVEY__NAME: ELECTION_JSON_KEY__WEBSURVEY,

    })


def _create_context_for_election_nominees_html(context):
    context.update({
        NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS__HTML_NAME: NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS,
    })


def _create_context_for_submission_buttons_html(context, create_new_election=False):
    context.update({
        SAVE_NEW_JSON_ELECTION__BUTTON_ID: SAVE_NEW_JSON_ELECTION__BUTTON_ID_VALUE,
        INPUT_REDIRECT_ELECTION__NAME: CREATE_NEW_ELECTION__NAME if create_new_election
        else UPDATE_EXISTING_ELECTION__NAME,
        INPUT_REDIRECT_ELECTION_SUBMIT__VALUE: SAVE_ELECTION__VALUE,
        SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID:
            SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID_VALUE,
        INPUT_REDIRECT_ELECTION_SUBMIT_AND_CONTINUE_EDITING__VALUE: SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE
    })
