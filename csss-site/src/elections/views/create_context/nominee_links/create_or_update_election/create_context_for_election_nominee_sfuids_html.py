from elections.views.Constants import NOMINEE_SFUIDS__VALUE, \
    NEW_NOMINEE_SFUIDS_FOR_NOMINEE_LINKS, REQUIRE_NOMINEE_SFUIDS, NOMINEE_SFUIDS__HTML_NAME


def create_context_for_election_nominee_sfuids_html(context, require_nominee_sfuids=True, nominee_sfuids=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/nominee_links/create_or_update_election/election_nominee_sfuids.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the election_nominee_sfuids.html
    require_nominee_sfuids -- indicates if the user has to specify nominee SFU IDs [for a new election]
     or can just modify existing SFU IDs [for existing nominee link election]
    nominee_sfuids -- the user inputted election nominee SFU IDs
    """
    context[NOMINEE_SFUIDS__HTML_NAME] = NEW_NOMINEE_SFUIDS_FOR_NOMINEE_LINKS
    context[REQUIRE_NOMINEE_SFUIDS] = require_nominee_sfuids
    if nominee_sfuids is not None:
        context[NOMINEE_SFUIDS__VALUE] = nominee_sfuids
