from django.shortcuts import render

from elections.models import NomineeLink
from elections.views.create_context.nominee_links.create_or_update_election.create_context_for_update_election_nominee_links_html import \
    create_context_for_update_election_nominee_links_html


def display_selected_election_and_nominee_links(request, election, context):
    """
    Display the selected election and its nominee links

    Keyword Argument
    request -- django request object
    election -- the election object for the election that has to be displayed
    context -- the context dictionary

    Return
    render object that direct the user to the page for updating an election in Nominee Link form
    """
    create_context_for_update_election_nominee_links_html(
        context, nominee_links=NomineeLink.objects.all(),
        election_date=election.date, election_time=election.date, election_type=election.election_type,
        websurvey_link=election.websurvey, create_new_election=election is None, election_obj=election
    )
    return render(
        request,
        'elections/nominee_links/create_or_update_election/update_election_nominee_links.html',
        context
    )
