import json
import json
import logging

from elections.models import Election
from elections.views.Constants import CURRENT_ELECTION, TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME, \
    TOGGLE_NOMINEE_LINKS_TO_DELETE, DRAFT_NOMINEE_LINKS, SAVED_NOMINEE_LINKS__HTML_NAME, DELETE__HTML_NAME, \
    SAVED_NOMINEE_LINK__ID__HTML_NAME, SAVED_NOMINEE_LINK__NAME__HTML_NAME, SAVED_NOMINEE_LINK__NOMINEE__HTML_NAME, \
    NO_NOMINEE_LINKED__HTML_NAME, CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINKS__HTML_NAME, \
    ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK, NOMINEE_LINK_ID__HTML_NAME, SAVED_NOMINEE_LINKS, DELETE, \
    SAVED_NOMINEE_LINK__ID, SAVED_NOMINEE_LINK__NAME, SAVED_NOMINEE_LINK__NOMINEE, NO_NOMINEE_LINKED, NOMINEE_LINK_ID, \
    NOMINEE_LINKS
from elections.views.create_context.nominee_links.create_context_for_display_errors_html import \
    create_context_for_display_errors_html
from elections.views.create_context.nominee_links.create_context_for_election_nominee_names_html import \
    create_context_for_election_nominee_names_html
from elections.views.create_context.nominee_links.create_context_for_submission_buttons_html import \
    create_context_for_submission_buttons_html
from elections.views.create_context.nominee_links.make_context_value_serializable_to_json import \
    make_context_value_json_serializable
from elections.views.create_context.webform_format.create_context_for_election_date_html import \
    create_context_for_election_date_html
from elections.views.create_context.webform_format.create_context_for_election_time_html import \
    create_context_for_election_time_html
from elections.views.create_context.webform_format.create_context_for_election_type_html import \
    create_context_for_election_type_html
from elections.views.create_context.webform_format.create_context_for_election_websurvey_html import \
    create_context_for_election_websurvey_html

logger = logging.getLogger('csss_site')


def create_context_for_update_election_nominee_links_html(
        context, error_messages=None, nominee_links=None, election_date=None, election_time=None, election_type=None,
        websurvey_link=None, create_new_election=False, draft_nominee_links=None,
        new_nominee_names=None, slug=None):
    require_nominee_names = (
            (nominee_links is None or len(nominee_links) == 0) and
            (draft_nominee_links is None or len(draft_nominee_links) == 0)
    )
    create_context_for_display_errors_html(context, error_messages=error_messages)
    context[CURRENT_ELECTION] = None if slug is None else Election.objects.get(slug=slug)
    create_context_for_election_date_html(context, election_date=election_date)
    create_context_for_election_time_html(context, election_time=election_time)
    create_context_for_election_type_html(context, election_type=election_type)
    create_context_for_election_websurvey_html(context, websurvey_link=websurvey_link)
    _create_context_for_nominee_links_table_html(context, draft_nominee_links=draft_nominee_links, slug=slug,
                                                 nominee_links=nominee_links)
    create_context_for_election_nominee_names_html(context, require_nominee_names=require_nominee_names,
                                                   nominee_names=new_nominee_names)
    create_context_for_submission_buttons_html(context, create_new_election=create_new_election)
    context[TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME] = TOGGLE_NOMINEE_LINKS_TO_DELETE
    logger.info(
        "[elections/create_nominee_links_context.py"
        " create_context_for_update_election_nominee_links_html()] "
        "context="
    )
    new_context = {key: make_context_value_json_serializable(value) for (key, value) in context.items()}
    logger.info(json.dumps(new_context, indent=3))


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
