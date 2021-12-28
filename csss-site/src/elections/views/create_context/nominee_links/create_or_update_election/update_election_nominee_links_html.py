import json
import logging

from csss.views.context_creation.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html
from elections.views.Constants import CURRENT_ELECTION, TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME, \
    TOGGLE_NOMINEE_LINKS_TO_DELETE
from elections.views.create_context.nominee_links.create_or_update_election.election_nominee_names_html import \
    create_context_for_election_nominee_names_html
from elections.views.create_context.nominee_links.create_or_update_election.update_election.create_context_for_nominee_links_table_html import \
    create_context_for_nominee_links_table_html
from elections.views.create_context.nominee_links.utils.make_context_value_serializable_to_json import \
    make_json_serializable_context_dictionary
from elections.views.create_context.webform_format.create_context_for_election_date_html import \
    create_context_for_election_date_html
from elections.views.create_context.webform_format.create_context_for_election_time_html import \
    create_context_for_election_time_html
from elections.views.create_context.webform_format.create_context_for_election_type_html import \
    create_context_for_election_type_html
from elections.views.create_context.webform_format.create_context_for_election_websurvey_html import \
    create_context_for_election_websurvey_html
from elections.views.create_context.webform_format.submission_buttons_html import \
    create_context_for_submission_buttons_html

logger = logging.getLogger('csss_site')


def create_context_for_update_election_nominee_links_html(
        context, error_messages=None, nominee_links=None, election_date=None, election_time=None, election_type=None,
        websurvey_link=None, create_new_election=False, draft_nominee_links=None,
        new_nominee_names=None, election=None):
    require_nominee_names = (
            (nominee_links is None or len(nominee_links) == 0) and
            (draft_nominee_links is None or len(draft_nominee_links) == 0)
    )
    create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=error_messages)
    context[CURRENT_ELECTION] = election
    create_context_for_election_date_html(context, election_date=election_date)
    create_context_for_election_time_html(context, election_time=election_time)
    create_context_for_election_type_html(context, election_type=election_type)
    create_context_for_election_websurvey_html(context, websurvey_link=websurvey_link)
    create_context_for_nominee_links_table_html(context, draft_nominee_links=draft_nominee_links,
                                                 nominee_links=nominee_links, election=election)
    create_context_for_election_nominee_names_html(context, require_nominee_names=require_nominee_names,
                                                   nominee_names=new_nominee_names)
    create_context_for_submission_buttons_html(context, create_new_election=create_new_election)
    context[TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME] = TOGGLE_NOMINEE_LINKS_TO_DELETE
    logger.info(
        "[elections/update_election_nominee_links_html.py"
        " create_context_for_update_election_nominee_links_html()] "
        "context="
    )
    new_context = make_json_serializable_context_dictionary(context)
    logger.info(json.dumps(new_context, indent=3))





