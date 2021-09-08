from django.shortcuts import render

from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from about.views.position_mapping_helper import update_context
from csss.views.context_creation.create_authenticated_contexts import create_context_for_updating_position_mappings
from csss.views.views import ERROR_MESSAGES_KEY


def officer_positions(request):
    html_page = 'about/officer_positions/officer_positions.html'
    context = create_context_for_updating_position_mappings(request, tab=TAB_STRING, html=html_page)
    context[ERROR_MESSAGES_KEY] = []

    return render(request, html_page, update_context(context))
