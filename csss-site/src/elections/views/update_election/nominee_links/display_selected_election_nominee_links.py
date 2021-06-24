from django.conf import settings
from django.shortcuts import render

from about.views.generate_officer_creation_links.officer_creation_link_management import HTML_PASSPHRASE_GET_KEY
from elections.models import NomineeLink, Election
from elections.views.create_context.nominee_links.create_nominee_links_context import \
    create_context_for_update_election_nominee_links_html


def display_selected_election_and_nominee_links(request, context, slug):
    """
    Display the selected election

    Keyword Argument
    request -- django request object
    context -- the context dictionary

    Return
    render object that direct the user to the page for updating an election in Nominee Link form, with possibly an
     error message
    """
    election = Election.objects.get(slug=slug)
    context.update(create_context_for_update_election_nominee_links_html(
        nominee_links=[set_nominee_link(nominee_link) for nominee_link in NomineeLink.objects.all()],
        election_date=election.date, election_time=election.date, election_type=election.election_type,
        websurvey_link=election.websurvey, create_new_election=election is None, slug=slug
    ))
    return render(request, 'elections/update_election/update_election_nominee_links.html', context)


def set_nominee_link(nominee_link):
    base_url = f"{settings.HOST_ADDRESS}"
    # this is necessary if the user is testing the site locally and therefore is using the port to access the
    # browser
    if settings.PORT is not None:
        base_url += f":{settings.PORT}"
    base_url += f"{settings.URL_ROOT}about/allow_officer_to_choose_name?"
    nominee_link.link = f"{base_url}{HTML_PASSPHRASE_GET_KEY}={nominee_link.passphrase}"
    return nominee_link
