from django.shortcuts import render

from elections.models import NomineeLink, Election
from elections.views.create_context.nominee_links.create_nominee_links_context import \
    create_context_for_update_election_nominee_links_html
from elections.views.utils.set_nominee_link import set_nominee_link


def display_selected_election_and_nominee_links(request, context, slug):
    """
    Display the selected election and its nominee links

    Keyword Argument
    request -- django request object
    context -- the context dictionary
    slug -- the slug of the election being displayed

    Return
    render object that direct the user to the page for updating an election in Nominee Link form
    """
    election = Election.objects.get(slug=slug)
    create_context_for_update_election_nominee_links_html(
        context, nominee_links=[set_nominee_link(nominee_link) for nominee_link in NomineeLink.objects.all()],
        election_date=election.date, election_time=election.date, election_type=election.election_type,
        websurvey_link=election.websurvey, create_new_election=election is None, slug=slug
    )
    return render(request, 'elections/update_election/update_election_nominee_links.html', context)


