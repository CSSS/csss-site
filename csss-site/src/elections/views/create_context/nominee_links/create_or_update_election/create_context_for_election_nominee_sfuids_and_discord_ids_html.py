from elections.views.Constants import NEW_NOMINEE_SFUIDS_AND_DISCORD_IDS_FOR_NOMINEE_LINKS, \
    NOMINEE_SFUIDS_AND_DISCORD_IDS__HTML_NAME, REQUIRE_NOMINEE_SFUIDS_AND_DISCORD_IDS, \
    NOMINEE_SFUIDS_AND_DISCORD_IDS__VALUE


def create_context_for_election_nominee_sfuids_and_discord_ids_html(
        context, require_nominee_sfuids_and_discord_ids=True, nominee_sfuids_and_discord_ids=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/nominee_links/create_or_update_election/election_nominee_sfuids_and_discord_ids.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the election_nominee_sfuids.html
    require_nominee_sfuids_and_discord_ids -- indicates if the user has to specify nominee SFU IDs and Discord IDs
     [for a new election] or can just modify existing SFU IDs and Discord IDs [for existing nominee link election]
    nominee_sfuids_and_discord_ids -- the user inputted election nominee SFU IDs and Discord IDs
    """
    context[NOMINEE_SFUIDS_AND_DISCORD_IDS__HTML_NAME] = NEW_NOMINEE_SFUIDS_AND_DISCORD_IDS_FOR_NOMINEE_LINKS
    context[REQUIRE_NOMINEE_SFUIDS_AND_DISCORD_IDS] = require_nominee_sfuids_and_discord_ids
    if nominee_sfuids_and_discord_ids is not None:
        context[NOMINEE_SFUIDS_AND_DISCORD_IDS__VALUE] = nominee_sfuids_and_discord_ids
