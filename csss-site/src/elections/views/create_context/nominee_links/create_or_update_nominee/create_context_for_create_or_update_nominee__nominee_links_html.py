import json
import logging

from csss.views.context_creation.error_htmls.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html
from elections.models import NomineeLink
from elections.views.Constants import NOMINEE__NAME__HTML_NAME, ELECTION_HUMAN_FRIENDLY_NAME__HTML_NAME
from elections.views.create_context.nominee_links.\
    create_or_update_nominee.create_context_for_form__nominee_links_html import \
    create_context_for_form__nominee_links_html
from elections.views.create_context.nominee_links.create_or_update_nominee.\
    create_context_for_view_saved_nominee_info_html import \
    create_context_for_view_saved_nominee_info_html
from elections.views.create_context.nominee_links.create_or_update_nominee.js_functions.on_load_js_functions.\
    create_context_for_main_function__nominee_links_html import \
    create_context_for_main_function__nominee_links_html
from elections.views.create_context.nominee_links.utils.make_context_value_serializable_to_json import \
    make_json_serializable_context_dictionary
from elections.views.create_context.webform_format.js_functions.create_context_for_add_blank_speech_html import \
    create_context_for_add_blank_speech_html
logger = logging.getLogger('csss_site')


def create_context_for_create_or_update_nominee__nominee_links_html(context, nominee_link_id=None,
                                                                    error_messages=None,
                                                                    nominee_info=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/nominee_links/create_or_update_nominee/create_or_update_nominee__nominee_links.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the create_or_update_nominee__nominee_links.html
    nominee_link_id -- the ID for the nominee link that has to be modified
    error_messages -- error message to display
    nominee_info -- the nominee info that the user inputted, otherwise None
    """
    create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=error_messages)

    nominee_link = NomineeLink.objects.get(id=nominee_link_id) \
        if len(list(NomineeLink.objects.all().filter(id=nominee_link_id))) == 1 else None
    nominee_obj = None
    if nominee_link is not None:
        context[ELECTION_HUMAN_FRIENDLY_NAME__HTML_NAME] = nominee_link.election.human_friendly_name
        nominee_obj = nominee_link.nominee
        if nominee_obj is not None:
            context[NOMINEE__NAME__HTML_NAME] = nominee_obj.name

    create_context_for_form__nominee_links_html(context)
    create_context_for_main_function__nominee_links_html(context, nominee_info=nominee_info, nominee_obj=nominee_obj)
    create_context_for_add_blank_speech_html(context)
    create_context_for_view_saved_nominee_info_html(context, nominee_obj=nominee_obj)
    logger.info(
        "[elections/create_context_for_create_or_update_nominee__nominee_links_html.py"
        " create_context_for_create_or_update_nominee__nominee_links_html()] "
        "context="
    )
    new_context = make_json_serializable_context_dictionary(context)
    logger.info(json.dumps(new_context, indent=3))
