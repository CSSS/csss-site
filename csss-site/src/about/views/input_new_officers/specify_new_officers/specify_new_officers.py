from django.shortcuts import render

from about.models import UnProcessedOfficer, OfficerEmailListAndPositionMapping
from about.views.Constants import TAB_STRING
from about.views.create_context.input_new_officers.create_context_for_specify_new_officers_html import \
    create_context_for_specify_new_officers_html
from about.views.input_new_officers.specify_new_officers.process_specified_new_officers import \
    process_specified_new_officers
from csss.setup_logger import get_logger
from csss.views.context_creation.create_authenticated_contexts import create_context_for_officer_creation_links


def specify_new_officers(request):
    """
    Shows the page where the user can select the year, term and positions for whom to create input info links
    """
    logger = get_logger()
    logger.info(f"[about/specify_new_officers.py specify_new_officers()] "
                f"request.POST={request.POST}")
    context = create_context_for_officer_creation_links(request, tab=TAB_STRING)
    process_election = request.method == 'POST'
    saved_unprocessed_officers = UnProcessedOfficer.objects.all()
    officer_emaillist_and_position_mappings = OfficerEmailListAndPositionMapping.objects.all()
    if process_election:
        return process_specified_new_officers(
            request, context, saved_unprocessed_officers, officer_emaillist_and_position_mappings
        )
    create_context_for_specify_new_officers_html(
        context, saved_unprocessed_officers, officer_emaillist_and_position_mappings
    )
    return render(request, 'about/input_new_officers/specify_new_officers.html', context)
