import json
import logging

from elections.views.create_context.nominee_links.utils.display_errors_html import \
    create_context_for_display_errors_html
from elections.views.create_context.nominee_links.utils.election_nominee_names_html import \
    create_context_for_election_nominee_names_html
from elections.views.create_context.nominee_links.utils.submission_buttons_html import \
    create_context_for_submission_buttons_html
from elections.views.create_context.webform_format.create_context_for_election_date_html import \
    create_context_for_election_date_html
from elections.views.create_context.webform_format.create_context_for_election_time_html import \
    create_context_for_election_time_html
from elections.views.create_context.webform_format.create_context_for_election_type_html import \
    create_context_for_election_type_html
from elections.views.create_context.webform_format.create_context_for_election_websurvey_html import \
    create_context_for_election_websurvey_html

logger = logging.getLogger('csss_site')


def create_context_for_create_election_nominee_links_html(context, election_date=None, election_time=None,
                                                          election_type=None, create_new_election=False,
                                                          websurvey_link=None, error_messages=None,
                                                          nominee_names=None):
    create_context_for_display_errors_html(context, error_messages)
    create_context_for_election_date_html(context, election_date=election_date)
    create_context_for_election_time_html(context, election_time=election_time)
    create_context_for_election_type_html(context, election_type=election_type)
    create_context_for_election_websurvey_html(context, websurvey_link=websurvey_link)
    create_context_for_election_nominee_names_html(context, nominee_names=nominee_names)
    create_context_for_submission_buttons_html(context, create_new_election=create_new_election)
    logger.info(
        "[elections/create_election_nominee_links_html.py"
        " create_context_for_create_election_nominee_links_html()] "
        "context="
    )
    logger.info(json.dumps(context, indent=3))

