import json

from django.shortcuts import render

from csss.setup_logger import Loggers
from csss.views.context_creation.create_authenticated_contexts import create_context_for_nominee_entering_their_info
from elections.models import NomineeLink
from elections.views.Constants import TAB_STRING, CREATE_OR_UPDATE_NOMINEE__NAME
from elections.views.create_context.nominee_links.create_or_update_nominee. \
    create_context_for_create_or_update_nominee__nominee_links_html import \
    create_context_for_create_or_update_nominee__nominee_links_html
from elections.views.update_election.nominee_links.process_nominee__nominee_links import \
    process_nominee__nominee_links


def display_and_process_html_for_nominee_modification_via_passphrase(request):
    logger = Loggers.get_logger()
    logger.info(
        "[elections/display_and_process_html_for_nominee_modification_via_passphrase__nominee_link.py"
        " display_and_process_html_for_nominee_modification_via_passphrase()] "
        "request.POST="
    )
    logger.info(json.dumps(request.POST, indent=3))
    context = create_context_for_nominee_entering_their_info(request, tab=TAB_STRING)

    nominee_links = NomineeLink.objects.all().filter(sfuid=request.user.username)
    error_message = None
    if nominee_links[0].election is None:
        error_message = [f"No election attached to Nominee Link {nominee_links[0]} detected in the request"]
    if error_message is not None:
        create_context_for_create_or_update_nominee__nominee_links_html(
            context, error_messages=[error_message], election_officer_request=False
        )
        return render(
            request, 'elections/nominee_links/create_or_update_nominee/create_or_update_nominee__nominee_links.html',
            context
        )

    if (request.method == "POST") and (CREATE_OR_UPDATE_NOMINEE__NAME in request.POST):
        return process_nominee__nominee_links(
            request, context, nominee_link=nominee_links[0], election_officer_request=False, passphrase=True
        )
    else:
        create_context_for_create_or_update_nominee__nominee_links_html(
            context, nominee_link_id=nominee_links[0].id, election_officer_request=False
        )
        return render(
            request, 'elections/nominee_links/create_or_update_nominee/create_or_update_nominee__nominee_links.html',
            context
        )
