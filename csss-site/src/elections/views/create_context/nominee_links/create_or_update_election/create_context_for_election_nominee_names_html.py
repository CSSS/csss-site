from elections.views.Constants import NOMINEE_NAMES__HTML_NAME, NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS, \
    REQUIRE_NOMINEE_NAMES, NOMINEE_NAMES__VALUE


def create_context_for_election_nominee_names_html(context, require_nominee_names=True, nominee_names=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/nominee_links/create_or_update_election/election_nominee_names.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the election_nominee_names.html
    require_nominee_names -- indicates if the user has to specify nominee names [for a new election]
     or can just modify existing names [for existing nominee link election]
    nominee_names -- the user inputted election nominee names
    """
    context[NOMINEE_NAMES__HTML_NAME] = NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS
    context[REQUIRE_NOMINEE_NAMES] = require_nominee_names
    if nominee_names is not None:
        context[NOMINEE_NAMES__VALUE] = nominee_names
