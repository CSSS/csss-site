from django.shortcuts import render

from about.models import OfficerEmailListAndPositionMapping
from csss.views.context_creation.create_vote_page_context import create_vote_page_context
from elections.models import NomineePosition, Voter, VoterChoice


def process_vote(request, context, latest_election):
    from querystring_parser import parser
    selected_positions = parser.parse(request.POST.urlencode())['selected_nominee']
    new, voter_obj = Voter.objects.get_or_create(sfuid=request.user.username, election=latest_election)
    position_names = list(
        NomineePosition.objects.all().filter(
            nominee_speech__nominee__election__slug=latest_election.slug
        ).distinct('position_name').values_list('position_name', flat=True)
    )
    # things to check, a position is specified only once
    # that a position can actually be selected in this election
    # that the nominee ID is valid for that position and election
    unique_selected_positions = list(set(list(selected_positions.keys())))
    if len(unique_selected_positions) != len(selected_positions):
        error_message = "It seems a position was selected more than once"
        create_vote_page_context(context, latest_election=latest_election, error_messages=[error_message],
                                 selected_positions=selected_positions,
                                 changes_pending=True)
        return render(request, 'elections/election_page.html', context)
    missing_positions = []
    valid_selected_positions = {}
    for position_name, nominated_officer_id in selected_positions.items():
        nominee_position = NomineePosition.objects.all().filter(
            id=int(nominated_officer_id), nominee_speech__nominee__election_id=latest_election.id
        ).first()
        error_message = None
        if nominee_position is None:
            error_message = f"Could not find the nominee position associated with id {nominated_officer_id}"
        elif nominee_position.position_name != position_name:
            error_message = f"Seems you incorrectly picked {nominee_position} for the {position_name}"

        if error_message:
            create_vote_page_context(context, latest_election=latest_election, error_messages=[error_message],
                                     selected_positions=selected_positions,
                                     changes_pending=True)
            return render(request, 'elections/election_page.html', context)
        else:
            valid_selected_positions[position_name] = int(nominated_officer_id)
    for position_name in position_names:
        if position_name not in valid_selected_positions:
            missing_positions.append(position_name)
    if len(missing_positions) > 0:
        missing_positions = list(OfficerEmailListAndPositionMapping.objects.all().filter(
            position_name__in=missing_positions
        ).order_by('position_index').values_list('position_name', flat=True))
        error_message = (
            "Seems you didn't pick a choice for all the positions. Missing a vote for: " +
            (", ".join(missing_positions))
        )
        create_vote_page_context(context, latest_election=latest_election, error_messages=[error_message],
                                 selected_positions=selected_positions,
                                 changes_pending=True)
        return render(request, 'elections/election_page.html', context)

    choices_so_far = {choice.nominee_position: choice for choice in voter_obj.voiterchoise_set.all()}
    outdated_choices = list(choices_so_far.values())
    for position_name, nominated_officer_id in valid_selected_positions.items():
        nominee_position = NomineePosition.objects.get(id=int(nominated_officer_id))
        if position_name in choices_so_far:
            choices_so_far[nominee_position].selection = nominee_position
            choices_so_far[nominee_position].save()
        else:
            VoterChoice(voter_obj, selection=nominee_position).save()
        outdated_choices.remove(nominated_officer_id)
    for outdated_choice in outdated_choices:
        NomineePosition.objects.get(id=outdated_choice).delete()
    create_vote_page_context(context, latest_election=latest_election)
    return render(request, 'elections/election_page.html', context)
