from elections.views.create_context.webform.js_functions.create_context_for_add_blank_speech_html import \
    create_context_for_add_blank_speech_html
from elections.views.create_context.webform_format.create_context_for_display_nominee_info_html import \
    create_context_for_display_nominee_info_html


def create_context_for_add_blank_nominee_html(
        context, webform_election=True, new_webform_election=True, include_id_for_nominee=False,
        draft_or_finalized_nominee_to_display=False):
    """
    populates the context dictionary that is used by elections/templates/elections/webform/js_functions/add_blank_nominee.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the add_blank_nominee.html
    webform_election -- bool to indicate if the election is a webform election
    new_webform_election -- bool to indicate if the election is a new webform election
    include_id_for_nominee -- bool to indicate if the html page has to show the ID for any of the nominees. Happens with saved elections
    draft_or_finalized_nominee_to_display -- bool to indicate if there is any nominee to show, either as a draft or saved
    """
    create_context_for_display_nominee_info_html(
        context, draft_or_finalized_nominee_to_display=draft_or_finalized_nominee_to_display,
        include_id_for_nominee=include_id_for_nominee, webform_election=webform_election,
        new_webform_election=new_webform_election,
        # nominee_obj=nominee_obj, nominee_info=nominee_info
    )
    create_context_for_add_blank_speech_html(context)
