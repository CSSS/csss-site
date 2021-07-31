from django.shortcuts import render

from elections.views.create_context.nominee_links.create_or_update_nominee__nominee_links_html import \
    create_context_for_update_nominee__nominee_links_html


def display_current_nominee_link_election(request, context, nominee_link_id):
    """
    Displays the selected nominee and their speech and select position names

    Keyword Argument
    request -- django request object
    context -- the context dictionary

    Return
    render object that directs the user to the page for updating a nominee via nominee link
    """
    create_context_for_update_nominee__nominee_links_html(context, nominee_link_id=nominee_link_id)
    return render(request,
                  'elections/update_nominee/update_nominee__nominee_links.html', context)
