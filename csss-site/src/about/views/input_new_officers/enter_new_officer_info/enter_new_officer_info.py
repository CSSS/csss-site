import logging

from django.shortcuts import render

from about.models import OfficerEmailListAndPositionMapping, UnProcessedOfficer
from about.views.Constants import TAB_STRING
from about.views.create_context.input_new_officers.enter_new_officer_info.create_context_for_enter_new_officer_info_html import \
    create_context_for_enter_new_officer_info_html
from about.views.input_new_officers.enter_new_officer_info.process_new_officer_info import process_new_officer_info
from csss.views.context_creation.create_authenticated_contexts import create_context_for_processing_unprocessed_officer

logger = logging.getLogger('csss_site')


def enter_new_officer_info(request):
    """
    Shows the page where the user can enter their info
    """
    logger.info(f"[about/enter_new_officer_info.py enter_new_officer_info()] "
                f"request.post_dict={request.POST}")
    context = create_context_for_processing_unprocessed_officer(request, tab=TAB_STRING)
    process_election = request.method == 'POST'
    officer_emaillist_and_position_mappings = OfficerEmailListAndPositionMapping.objects.all()
    unprocessed_officers = UnProcessedOfficer.objects.all()
    if process_election:
        return process_new_officer_info(
            request, context, officer_emaillist_and_position_mappings, unprocessed_officers
        )
    create_context_for_enter_new_officer_info_html(
        context, request.user.username, officer_emaillist_and_position_mappings, unprocessed_officers
    )
    return render(request, 'about/input_new_officers/enter_new_officer_info/enter_new_officer_info.html', context)
