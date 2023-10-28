from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.views.context_creation.create_authenticated_contexts import create_context_for_voting
from csss.views.context_creation.create_vote_page_context import create_vote_page_context
from csss.views.pstdatetime import pstdatetime
from elections.models import Election
from elections.views.Constants import TAB_STRING
from elections.views.endpoints.process_vote import process_vote


def vote(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f"{settings.URL_ROOT}login?next={request.path}")
    context = create_context_for_voting(request, tab=TAB_STRING)
    latest_election = Election.objects.all().order_by('-date').first()
    error_messages = None
    can_vote = True
    if not validate_vote_request(context, latest_election):
        error_messages = [f"No live election detected"]
        can_vote = False
    elif request.method == 'POST':
        return process_vote(request, context, latest_election)
    create_vote_page_context(
        context, latest_election=latest_election, error_messages=error_messages, can_vote=can_vote
    )
    return render(request, 'elections/election_page.html', context)


def validate_vote_request(context, latest_election):
    today_date = pstdatetime.now().pst
    time_to_vote = (
        latest_election.end_date is not None and latest_election.date is not None and
        latest_election.date <= today_date <= latest_election.end_date
    )
    time_to_vote = True
    return not context['current_election_officer'] and time_to_vote
