import logging

from django.shortcuts import render

from about.views.create_context.specify_new_officers.create_context_for_specify_new_officers_html import \
    create_context_for_specify_new_officers_html
from about.views.input_new_officers.specify_new_officers.process_specified_new_officers import process_specified_new_officers
from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from csss.views.context_creation.create_authenticated_contexts import create_context_for_officer_creation_links

logger = logging.getLogger('csss_site')


def specify_new_officers(request):
    """
    Shows the page where the user can select the year, term and positions for whom to create input info links
    """
    logger.info(f"[about/specify_new_officers.py specify_new_officers()] "
                f"request.POST={request.POST}")
    context = create_context_for_officer_creation_links(request, tab=TAB_STRING)
    process_election = request.method == 'POST'
    if process_election:
        return process_specified_new_officers(request, context)
    create_context_for_specify_new_officers_html(context)
    return render(request, 'about/input_new_officers/specify_new_officers.html', context)
