from csss.views.context_creation.create_main_context import create_main_context, CURRENT_ELECTION_OFFICER
from csss.views.determine_user_role import user_is_current_election_officer


def create_election_page_context(request, tab=None):
    """
    Created the context for the election page by tacking on the flag of whether or not the user
     is the current election officer to the context dictionary and by returning it as a separate variable
      so that the election_page.py file does not need to use the CURRENT_ELECTION_OFFICER key

    Keyword Arguments
    request -- the django request object
    tab -- the tab that needs to be specified it the context


    Return
    context -- the base context dictionary with the election officer indicator
    current_election_officer -- flag to indicate if user is the current election officer
    """
    context = create_main_context(request, tab=tab)
    context[CURRENT_ELECTION_OFFICER] = user_is_current_election_officer(request)
    return context, context[CURRENT_ELECTION_OFFICER]
