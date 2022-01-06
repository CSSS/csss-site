from elections.views.Constants import DRAFT_NOMINEE_LINKS, NOMINEE_LINKS
from elections.views.create_context.nominee_links.create_or_update_election.update_election.nominee_links_table.\
    create_context_for_draft_nominee_links_html import \
    create_context_for_draft_nominee_links_html
from elections.views.create_context.nominee_links.create_or_update_election.update_election.nominee_links_table.\
    create_context_for_final_nominee_links_html import \
    create_context_for_final_nominee_links_html


def create_context_for_nominee_links_table_html(
        context, draft_nominee_links=None, nominee_links=None, election_obj=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/nominee_links/create_or_update_election/update_election/nominee_links_table.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the nominee_links_table.html
    draft_nominee_links -- nominee links that are not yet saved and still have work pending and will be used in
     elections/templates/elections/nominee_links/create_or_update_election/update_election/
     nominee_links_table/draft_nominee_links.html
    nominee_links -- finalized nominee links that will be used in elections/templates/elections/nominee_links/
     create_or_update_election/update_election/nominee_links_table/final_nominee_links.html
    election_obj -- the object for the current election to determine which saved nominee links map
     to which draft nominee links
    """
    if draft_nominee_links is not None:
        context[DRAFT_NOMINEE_LINKS] = draft_nominee_links
    context[NOMINEE_LINKS] = nominee_links
    create_context_for_draft_nominee_links_html(
        context, draft_nominee_links=draft_nominee_links, election_obj=election_obj
    )
    create_context_for_final_nominee_links_html(context, nominee_links=nominee_links)
