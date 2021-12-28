from elections.views.Constants import NOMINEE_NAMES__HTML_NAME, NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS, \
    REQUIRE_NOMINEE_NAMES, NOMINEE_NAMES__VALUE


def create_context_for_election_nominee_names_html(context, require_nominee_names=True, nominee_names=None):
    context[NOMINEE_NAMES__HTML_NAME] = NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS
    context[REQUIRE_NOMINEE_NAMES] = require_nominee_names
    if nominee_names is not None:
        context[NOMINEE_NAMES__VALUE] = nominee_names
