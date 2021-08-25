from administration.Constants import ELECTION_MANAGEMENT_GROUP_NAME
from csss.views.context_creation.create_base_context import create_base_context
from elections.models import Election


def create_main_context(request, tab, groups=None):
    """
    creates the main context dictionary

    Keyword Arguments
    request -- the django request object
    tab -- the tab that needs to be specified it the context
    groups -- the groups that need to be checked to see if the user is allowed to certain group privileges

    Return
    context -- the base context dictionary
    """
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    elections = Election.objects.all().order_by('-date')
    if len(elections) == 0:
        elections = None
    context = create_base_context()
    context.update({
        'authenticated': request.user.is_authenticated,
        'authenticated_officer': ('officer' in groups),
        ELECTION_MANAGEMENT_GROUP_NAME: (ELECTION_MANAGEMENT_GROUP_NAME in groups),
        'staff': request.user.is_staff,
        'username': request.user.username,
        'tab': tab,
        'election_list': elections
    })
    return context
