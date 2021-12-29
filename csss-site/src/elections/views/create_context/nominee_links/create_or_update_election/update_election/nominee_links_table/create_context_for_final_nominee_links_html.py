from elections.views.Constants import NOMINEE_LINKS, SAVED_NOMINEE_LINKS__HTML_NAME, SAVED_NOMINEE_LINKS, \
    DELETE__HTML_NAME, DELETE, SAVED_NOMINEE_LINK__ID__HTML_NAME, SAVED_NOMINEE_LINK__ID, \
    SAVED_NOMINEE_LINK__NAME__HTML_NAME, SAVED_NOMINEE_LINK__NAME, SAVED_NOMINEE_LINK__NOMINEE__HTML_NAME, \
    SAVED_NOMINEE_LINK__NOMINEE, NO_NOMINEE_LINKED__HTML_NAME, NO_NOMINEE_LINKED, \
    TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME, TOGGLE_NOMINEE_LINKS_TO_DELETE, \
    CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINKS__HTML_NAME, ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK, \
    NOMINEE_LINK_ID__HTML_NAME, NOMINEE_LINK_ID


def create_context_for_final_nominee_links_html(context, nominee_links=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/nominee_links/create_or_update_election/
     update_election/nominee_links_table/final_nominee_links.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the final_nominee_links.html
    nominee_links -- finalized nominee links
    """
    context[NOMINEE_LINKS] = nominee_links
    context[SAVED_NOMINEE_LINKS__HTML_NAME] = SAVED_NOMINEE_LINKS
    context[DELETE__HTML_NAME] = DELETE
    context[SAVED_NOMINEE_LINK__ID__HTML_NAME] = SAVED_NOMINEE_LINK__ID
    context[SAVED_NOMINEE_LINK__NAME__HTML_NAME] = SAVED_NOMINEE_LINK__NAME
    context[SAVED_NOMINEE_LINK__NOMINEE__HTML_NAME] = SAVED_NOMINEE_LINK__NOMINEE
    context[NO_NOMINEE_LINKED__HTML_NAME] = NO_NOMINEE_LINKED
    context[TOGGLE_NOMINEE_LINKS_TO_DELETE__HTML_CLASS_NAME] = TOGGLE_NOMINEE_LINKS_TO_DELETE
    context[CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINKS__HTML_NAME] = \
        ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK
    context[NOMINEE_LINK_ID__HTML_NAME] = NOMINEE_LINK_ID
