from django.shortcuts import render

from csss.views_helper import verify_access_logged_user_and_create_context_for_elections, ERROR_MESSAGE_KEY
from elections.views.Constants import TAB_STRING
from elections.views.utils.get_list_of_elections import get_list_of_elections


def show_page_where_user_can_select_election_to_update(request):
    """
    Shows the page where the user can choose an election and whether they want to update it via JSON or WebForm
    """
    (render_value, error_message, context) = verify_access_logged_user_and_create_context_for_elections(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    context.update(get_list_of_elections())
    return render(request, 'elections/update_election/list_elections_to_modify.html', context)
