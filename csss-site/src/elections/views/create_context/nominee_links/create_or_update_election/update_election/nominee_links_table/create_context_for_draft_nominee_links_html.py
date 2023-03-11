from elections.views.Constants import DRAFT_NOMINEE_LINKS, SAVED_NOMINEE_LINKS__HTML_NAME, SAVED_NOMINEE_LINKS, \
    DELETE__HTML_NAME, DELETE, SAVED_NOMINEE_LINK__ID__HTML_NAME, SAVED_NOMINEE_LINK__ID, \
    SAVED_NOMINEE_LINK__NOMINEE__HTML_NAME, \
    SAVED_NOMINEE_LINK__NOMINEE, NO_NOMINEE_LINKED__HTML_NAME, NO_NOMINEE_LINKED, \
    TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME, TOGGLE_NOMINEE_LINKS_TO_DELETE, CURRENT_ELECTION, \
    CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINKS__HTML_NAME, ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK, \
    NOMINEE_LINK_ID__HTML_NAME, NOMINEE_LINK_ID, SAVED_NOMINEE_LINK__SFUID__HTML_NAME, SAVED_NOMINEE_LINK__SFUID, \
    SAVED_NOMINEE_LINK__DISCORD_ID__HTML_NAME, SAVED_NOMINEE_LINK__DISCORD_ID


def create_context_for_draft_nominee_links_html(context, draft_nominee_links=None, election_obj=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/nominee_links/create_or_update_election/update_election/
     nominee_links_table/draft_nominee_links.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the draft_nominee_links.html
    draft_nominee_links -- nominee links that are not yet saved and still have work pending
    election_obj -- the object for the current election to determine which saved nominee links map
     to which draft nominee links
    """
    if draft_nominee_links is not None:
        context[DRAFT_NOMINEE_LINKS] = draft_nominee_links
    context[SAVED_NOMINEE_LINKS__HTML_NAME] = SAVED_NOMINEE_LINKS
    context[DELETE__HTML_NAME] = DELETE
    context[SAVED_NOMINEE_LINK__ID__HTML_NAME] = SAVED_NOMINEE_LINK__ID
    context[SAVED_NOMINEE_LINK__SFUID__HTML_NAME] = SAVED_NOMINEE_LINK__SFUID
    context[SAVED_NOMINEE_LINK__DISCORD_ID__HTML_NAME] = SAVED_NOMINEE_LINK__DISCORD_ID
    context[SAVED_NOMINEE_LINK__NOMINEE__HTML_NAME] = SAVED_NOMINEE_LINK__NOMINEE
    context[NO_NOMINEE_LINKED__HTML_NAME] = NO_NOMINEE_LINKED
    context[TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME] = TOGGLE_NOMINEE_LINKS_TO_DELETE
    context[CURRENT_ELECTION] = election_obj
    context[CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINKS__HTML_NAME] = \
        ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK
    context[NOMINEE_LINK_ID__HTML_NAME] = NOMINEE_LINK_ID
