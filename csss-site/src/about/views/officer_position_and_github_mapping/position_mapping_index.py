from django.shortcuts import render

from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from about.views.position_mapping_helper import update_context
from csss.views.exceptions import ERROR_MESSAGES_KEY
from csss.views_helper import create_context_for_officers


def position_mapping(request):
    html_page = 'about/position_mapping/position_mapping.html'
    context = create_context_for_officers(
        request, TAB_STRING, html=html_page, context_function=update_context
    )
    context[ERROR_MESSAGES_KEY] = []

    return render(request, html_page, update_context(context))
