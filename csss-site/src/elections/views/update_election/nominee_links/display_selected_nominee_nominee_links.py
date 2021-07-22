from django.shortcuts import render

from elections.views.create_context.nominee_links.create_nominee_links_context import \
    create_context_for_update_nominee_html


def display_current_nominee_link_election(request, context, nominee_link_id):
    create_context_for_update_nominee_html(context, nominee_link_id=nominee_link_id)
    return render(request,
                  'elections/update_nominee/update_nominee__nominee_links.html', context)
