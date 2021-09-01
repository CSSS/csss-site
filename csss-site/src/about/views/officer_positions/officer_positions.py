from django.shortcuts import render

from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from about.views.position_mapping_helper import update_context
from csss.views.context_creation.create_main_context import create_main_context
from csss.views.exceptions import ERROR_MESSAGES_KEY
from csss.views.request_validation import validate_officer_request


def officer_positions(request):
    html_page = 'about/officer_positions/officer_positions.html'
    validate_officer_request(request, html=html_page)
    context = create_main_context(request, TAB_STRING)
    context[ERROR_MESSAGES_KEY] = []

    return render(request, html_page, update_context(context))
