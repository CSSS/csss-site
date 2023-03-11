import json

from django.shortcuts import render

from csss.setup_logger import Loggers
from csss.views.context_creation.create_main_context import create_main_context
from elections.models import NomineeLink
from elections.views.Constants import TAB_STRING, CREATE_OR_UPDATE_NOMINEE__NAME, HTML_PASSPHRASE_GET_KEY
from elections.views.create_context.nominee_links.create_or_update_nominee.\
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
    context = create_main_context(request, TAB_STRING)

    nominee_link_passphrase = request.GET.get(HTML_PASSPHRASE_GET_KEY, None)
    nominee_links = NomineeLink.objects.all().filter(passphrase=nominee_link_passphrase)
    error_message = None
    if nominee_link_passphrase is None:
        error_message = ["Unable to locate the Nominee Link passphrase in the request"]
    elif len(nominee_links) != 1:
        error_message = [f"invalid Nominee Link passphrase of {nominee_link_passphrase} detected in the request"]
    elif nominee_links[0].election is None:
        error_message = [f"No election attached to Nominee Link {nominee_links[0]} detected in the request"]
    if error_message is not None:
        create_context_for_create_or_update_nominee__nominee_links_html(context, error_messages=[error_message])
        return render(
            request, 'elections/nominee_links/create_or_update_nominee/create_or_update_nominee__nominee_links.html',
            context
        )

    if (request.method == "POST") and (CREATE_OR_UPDATE_NOMINEE__NAME in request.POST):
        return process_nominee__nominee_links(
            request, context, nominee_link=nominee_links[0], election_officer_request=False, passphrase=True
        )
    else:
        create_context_for_create_or_update_nominee__nominee_links_html(context, nominee_link_id=nominee_links[0].id)
        return render(
            request, 'elections/nominee_links/create_or_update_nominee/create_or_update_nominee__nominee_links.html',
            context
        )
