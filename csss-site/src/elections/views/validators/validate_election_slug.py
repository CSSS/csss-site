from elections.models import Election


def validate_election_slug(slug):
    """
    Ensure that the given slug is attached to only one election

    Keyword Argument
    slug -- the slug to check

    Return
    bool -- True or False to indicate if there is only one election with the given slug
    """
    return len(Election.objects.all().filter(slug=slug)) == 1
