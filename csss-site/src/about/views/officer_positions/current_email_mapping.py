from django.shortcuts import render

from about.models import OfficerEmailListAndPositionMapping
from about.views.Constants import TAB_STRING
from about.views.create_context.officer_positions.create_context_for_current_email_mappings_html import \
    create_context_for_current_email_mappings_html
from csss.views.context_creation.create_authenticated_contexts import create_context_for_officer_email_mappings


def current_email_mapping(request):
    context = create_context_for_officer_email_mappings(request, tab=TAB_STRING)
    officer_emaillist_and_position_mappings = OfficerEmailListAndPositionMapping.objects.all()
    create_context_for_current_email_mappings_html(context, officer_emaillist_and_position_mappings)
    return render(request, 'about/officer_positions/current_email_mappings.html', context)