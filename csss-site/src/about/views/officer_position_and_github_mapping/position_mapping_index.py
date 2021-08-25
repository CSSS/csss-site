from django.shortcuts import render

from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from about.views.position_mapping_helper import update_context
from csss.views.request_validation import verify_access_logged_user_and_create_context
from csss.views_helper import ERROR_MESSAGE_KEY, ERROR_MESSAGES_KEY


def position_mapping(request):
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request,
                                                                                          TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = f'{error_message}<br>'
        return render_value
    context[ERROR_MESSAGES_KEY] = []

    return render(request, 'about/position_mapping/position_mapping.html', update_context(context))
