import datetime
import logging

from csss.views_helper import ERROR_MESSAGES_KEY
from elections.models import Election
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
    REQUIRE_NOMINEE_NAMES, TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME, TOGGLE_NOMINEE_LINKS_TO_DELETE

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
