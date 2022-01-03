import json
import logging

from csss.views.context_creation.error_htmls.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html
from elections.models import NomineeLink
from elections.views.Constants import PRE_EXISTING_ELECTION
from elections.views.create_context.nominee_links.create_or_update_election.\
    create_context_for_election_nominee_names_html import \
    create_context_for_election_nominee_names_html
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


def create_context_for_create_election_nominee_links_html(context, election_date=None, election_time=None,
                                                          election_type=None, create_new_election=False,
                                                          websurvey_link=None, error_messages=None,
                                                          nominee_names=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/nominee_links/create_or_update_election/create_election_nominee_links.html
    Keyword Arguments
    context -- the context dictionary that has to be populated for the create_election_nominee_links.html
    election_date -- the date of the election that the user inputted, otherwise None
    election_time -- the time of the election that the user inputted, otherwise None
    election_type -- the election type that the user inputted, otherwise None
    create_new_election -- boolean to indicate what the submission button should be labelled with
    websurvey_link -- the websurvey link of the election that the user inputted, otherwise None
    error_messages -- error message to display
    nominee_names --the nominee names that the user inputted so far
    """
    pre_existing_election = False
    if create_new_election:
        nominee_links = NomineeLink.objects.all()
        if len(nominee_links) > 0:
            pre_existing_election = True
            error_messages = [(
                f"Please delete the nominee links for the {nominee_links[0].election.human_friendly_name} "
                f"election before creating a new election via nominee link"
            )]
    create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=error_messages)
    context[PRE_EXISTING_ELECTION] = pre_existing_election
    if pre_existing_election is False:
        create_context_for_election_date_html(context, election_date=election_date)
        create_context_for_election_time_html(context, election_time=election_time)
        create_context_for_election_type_html(context, election_type=election_type)
        create_context_for_election_websurvey_html(context, websurvey_link=websurvey_link)
        create_context_for_election_nominee_names_html(context, nominee_names=nominee_names)
        create_context_for_submission_buttons_html(context, create_new_election=create_new_election)
    logger.info(
        "[elections/create_context_for_create_election_nominee_links_html.py"
        " create_context_for_create_election_nominee_links_html()] "
        "context="
    )
    json_serializable_context = make_json_serializable_context_dictionary(context)
    logger.info(json.dumps(json_serializable_context, indent=3))
