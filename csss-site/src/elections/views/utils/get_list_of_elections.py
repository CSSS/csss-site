from elections.models import Election


def get_list_of_elections():
    """
    Gets the elections that need to be displayed that can be modified by the user

    Return
    dictionary where the key is 'elections' and the value is the list of elections, or None
    """
    elections = Election.objects.all().order_by('-date')
    return {
        'elections': None if len(elections) == 0 else elections
    }
