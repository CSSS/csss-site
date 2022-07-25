from django.shortcuts import render

from about.views.Constants import TAB_STRING
from about.views.position_mapping_helper import update_context
from csss.views.context_creation.create_authenticated_contexts import \
    create_context_for_updating_github_mappings_and_permissions
from csss.views.views import ERROR_MESSAGES_KEY


def github_mapping(request):
    context = create_context_for_updating_github_mappings_and_permissions(request, tab=TAB_STRING)
    context[ERROR_MESSAGES_KEY] = []

    return render(request, 'about/github_position_mapping/github_position_mapping.html', update_context(context))
