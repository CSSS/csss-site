import json

from django.conf import settings

from csss.setup_logger import Loggers
from csss.views.context_creation.error_htmls.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html
from elections.views.Constants import CURRENT_ELECTION, TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME, \
    TOGGLE_NOMINEE_LINKS_TO_DELETE, DRAFT_NOMINEE_LINKS, NOMINEE_LINKS, \
    ENDPOINT_CREATE_OR_UPDATE_NOMINEE_FOR_NOMINEE_VIA_LOGIN__NOMINEE_LINK, LINK_FOR_NOMINEES_TO_ENTER_INFO
from elections.views.create_context.nominee_links.create_or_update_election.\
    create_context_for_election_nominee_sfuids_and_discord_ids_html import \
    create_context_for_election_nominee_sfuids_and_discord_ids_html
from elections.views.create_context.nominee_links.create_or_update_election.update_election. \
    create_context_for_nominee_links_table_html import \
    create_context_for_nominee_links_table_html
from elections.views.create_context.nominee_links.utils.make_context_value_serializable_to_json import \
    make_json_serializable_context_dictionary
from elections.views.create_context.webform_format.create_context_for_election_date_html import \
    create_context_for_election_date_html
from elections.views.create_context.webform_format.create_context_for_election_end_date_html import \
    create_context_for_election_end_date_html
from elections.views.create_context.webform_format.create_context_for_election_time_html import \
    create_context_for_election_time_html
from elections.views.create_context.webform_format.create_context_for_election_type_html import \
    create_context_for_election_type_html
from elections.views.create_context.webform_format.create_context_for_election_websurvey_html import \
    create_context_for_election_websurvey_html
from elections.views.create_context.webform_format.create_context_for_submission_buttons_html import \
    create_context_for_submission_buttons_html


def create_context_for_update_election_nominee_links_html(
    context, error_messages=None, nominee_links=None, election_date=None, election_time=None, election_end_date=None,
    election_type=None, websurvey_link=None, create_new_election=False, draft_nominee_links=None,
        new_nominee_sfuids_and_discord_ids=None, election_obj=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/nominee_links/create_or_update_election/update_election_nominee_links.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the update_election_nominee_links.html
    error_messages -- error message to display
    nominee_links -- finalized nominee links that will be used in elections/templates/elections/nominee_links/
     create_or_update_election/update_election/nominee_links_table/final_nominee_links.html
    election_date -- the user inputted election date
    election_time -- the user inputted election time
    election_end_date -- the user inputted election end date
    election_type -- the user inputted election type
    websurvey_link -- the user inputted election websurvey link
    create_new_election -- boolean to indicate what the submission button should be labelled with
    draft_nominee_links -- nominee links that are not yet saved and still have work pending and will be used in
     elections/templates/elections/nominee_links/create_or_update_election/update_election/
     nominee_links_table/draft_nominee_links.html
    new_nominee_sfuids_and_discord_ids -- the user inputted election nominee SFU IDs and Discord IDs
    election_obj -- the object for the current election to determine which saved nomin e links map
     to which draft nominee links
    """
    logger = Loggers.get_logger()
    require_nominee_sfuids_and_discord_ids = (
        (nominee_links is None or len(nominee_links) == 0) and
        (draft_nominee_links is None or len(draft_nominee_links) == 0)
    )
    create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=error_messages)
    context[CURRENT_ELECTION] = election_obj
    create_context_for_election_date_html(context, election_date=election_date)
    create_context_for_election_time_html(context, election_time=election_time)
    create_context_for_election_end_date_html(context, election_end_date=election_end_date)
    create_context_for_election_type_html(context, election_type=election_type)
    create_context_for_election_websurvey_html(context, websurvey_link=websurvey_link)

    base_url = f"{settings.HOST_ADDRESS}"
    # this is necessary if the user is testing the site locally and therefore is using the port to access the
    # browser
    if settings.PORT is not None:
        base_url += f":{settings.PORT}"
    context[LINK_FOR_NOMINEES_TO_ENTER_INFO] = (
        f"http://{base_url}{settings.URL_ROOT}login?next=/elections/"
        f"{ENDPOINT_CREATE_OR_UPDATE_NOMINEE_FOR_NOMINEE_VIA_LOGIN__NOMINEE_LINK}"
    )
    create_context_for_nominee_links_table_html(context, draft_nominee_links=draft_nominee_links,
                                                nominee_links=nominee_links, election_obj=election_obj)
    if draft_nominee_links is not None:
        context[DRAFT_NOMINEE_LINKS] = draft_nominee_links
    context[NOMINEE_LINKS] = nominee_links
    create_context_for_election_nominee_sfuids_and_discord_ids_html(
        context, require_nominee_sfuids_and_discord_ids=require_nominee_sfuids_and_discord_ids,
        nominee_sfuids_and_discord_ids=new_nominee_sfuids_and_discord_ids
    )
    create_context_for_submission_buttons_html(context, create_new_election=create_new_election)
    context[TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME] = TOGGLE_NOMINEE_LINKS_TO_DELETE
    logger.info(
        "[elections/create_context_for_update_election_nominee_links_html.py"
        " create_context_for_update_election_nominee_links_html()] "
        "context="
    )
    new_context = make_json_serializable_context_dictionary(context)
    logger.info(json.dumps(new_context, indent=3))
