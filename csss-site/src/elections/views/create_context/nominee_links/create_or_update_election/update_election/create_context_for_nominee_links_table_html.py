from elections.views.create_context.nominee_links.create_or_update_election.update_election.nominee_links_table.create_context_for_draft_nominee_links_html import \
    create_context_for_draft_nominee_links_html
from elections.views.create_context.nominee_links.create_or_update_election.update_election.nominee_links_table.create_context_for_final_nominee_links_html import \
    create_context_for_final_nominee_links_html


def create_context_for_nominee_links_table_html(
        context, draft_nominee_links=None, nominee_links=None, election=None):
    create_context_for_draft_nominee_links_html(context, draft_nominee_links=draft_nominee_links, election=election)
    create_context_for_final_nominee_links_html(context, nominee_links=nominee_links)

