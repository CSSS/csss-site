import json

from django.shortcuts import render

from csss.setup_logger import get_logger
from csss.views.context_creation.create_authenticated_contexts import create_context_for_election_officer
from elections.models import NomineeLink
from elections.views.Constants import TAB_STRING, NOMINEE_LINK_ID, CREATE_OR_UPDATE_NOMINEE__NAME
from elections.views.create_context.nominee_links.create_or_update_nominee. \
    create_context_for_create_or_update_nominee__nominee_links_html import \
    create_context_for_create_or_update_nominee__nominee_links_html
from elections.views.update_election.nominee_links.process_nominee__nominee_links import \
    process_nominee__nominee_links

logger = get_logger()


def display_and_process_html_for_nominee_modification(request):
    logger.info(
        "[elections/display_and_process_html_for_nominee_modification__nominee_link.py"
        " display_and_process_html_for_nominee_modification()] "
        "request.POST="
    )
    logger.info(json.dumps(request.POST, indent=3))
    context = create_context_for_election_officer(request, tab=TAB_STRING)

    nominee_link_id = request.GET.get(NOMINEE_LINK_ID, None)
    nominee_links = NomineeLink.objects.all().filter(id=nominee_link_id)
    error_message = None
    if nominee_link_id is None:
        error_message = ["Unable to locate the Nominee Link ID in the request"]
    elif len(nominee_links) != 1:
        error_message = [f"invalid Nominee Link ID of {nominee_link_id} detected in the request"]
    elif nominee_links[0].election is None:
        error_message = [f"No election attached to Nominee Link {nominee_links[0]} detected in the request"]
    if error_message is not None:
        create_context_for_create_or_update_nominee__nominee_links_html(context, error_messages=[error_message])
        return render(
            request, 'elections/nominee_links/create_or_update_nominee/create_or_update_nominee__nominee_links.html',
            context
        )

    if (request.method == "POST") and (CREATE_OR_UPDATE_NOMINEE__NAME in request.POST):
        return process_nominee__nominee_links(request, context, nominee_links[0])
    else:
        create_context_for_create_or_update_nominee__nominee_links_html(context, nominee_link_id=nominee_link_id)
        return render(
            request, 'elections/nominee_links/create_or_update_nominee/create_or_update_nominee__nominee_links.html',
            context
        )
