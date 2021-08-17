from django.shortcuts import render

from about.views.officer_position_and_github_mapping.officer_management_helper import TAB_STRING
from about.views.position_mapping_helper import update_context
from administration.views.validate_auth import requires_role
from administration.views.verify_user_access import verify_user_can_update_position_mappings
from csss.views_helper import ERROR_MESSAGE_KEY, ERROR_MESSAGES_KEY


@requires_role(["Webmaster", 'Director of Archives'])
def position_mapping(request):
    (render_value, error_message, context) = verify_user_can_update_position_mappings(
        request, TAB_STRING
    )
    if render_value is not None:
        request.session[ERROR_MESSAGE_KEY] = f'{error_message}<br>'
        return render_value
    context[ERROR_MESSAGES_KEY] = []

    return render(request, 'about/position_mapping/position_mapping.html', update_context(context))
