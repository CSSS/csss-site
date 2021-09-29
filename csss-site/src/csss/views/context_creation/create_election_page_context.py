from csss.views.context_creation.create_main_context import create_main_context, CURRENT_ELECTION_OFFICER
from csss.views.determine_user_role import user_is_current_election_officer


def create_election_page_context(request, tab=None):
    context = create_main_context(request, tab)
    context[CURRENT_ELECTION_OFFICER] = user_is_current_election_officer(request)
    return context
