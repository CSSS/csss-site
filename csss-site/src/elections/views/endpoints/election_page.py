from django.conf import settings
from django.shortcuts import render

from csss.setup_logger import Loggers
from csss.views.context_creation.create_election_page_context import create_election_page_context
from csss.views.views import ERROR_MESSAGES_KEY
from csss.views_helper import get_current_date
from elections.models import Election, NomineePosition, NomineeLink, VoterChoice
from elections.views.Constants import TAB_STRING, ELECTION__HTML_NAME, \
    PRE_EXISTING_ELECTION, DELETE_EXISTING_NOMINEE_LINKS_MESSAGE, \
    ENDPOINT_DELETE_NOMINEE_LINKS, DELETE_NOMINEE_LINKS_REDIRECT_PATH_KEY, NO_CONFIDENCE_NAME, SKIPPED_VOTE, \
    POSITIONS_LIST_HTML__NAME
from elections.views.validators.validate_election_slug import validate_election_slug


def get_nominees(request, slug):
    logger = Loggers.get_logger()
    context, user_is_election_officer = create_election_page_context(request, TAB_STRING)
    if not validate_election_slug(slug):
        context[ERROR_MESSAGES_KEY] = ["specified slug has an incorrect number of elections attached to it."]
        return render(request, 'elections/election_page.html', context)
    election_to_display = Election.objects.get(slug=slug)
    if user_is_election_officer:
        privilege_message = "user does have election management privilege"
    else:
        privilege_message = "user does not have election management privilege"
    logger.info(f"[elections/election_page.py get_nominees()] determining if election with slug {slug}"
                f"needs to be shown as its date is {election_to_display.date} and the {privilege_message}")
    if election_to_display.date <= get_current_date() or user_is_election_officer:
        if user_is_election_officer:
            nominee_links = NomineeLink.objects.all().exclude(election__slug=slug)
            context[PRE_EXISTING_ELECTION] = False
            if len(nominee_links) > 0:
                context.update({
                    PRE_EXISTING_ELECTION: True,
                    DELETE_EXISTING_NOMINEE_LINKS_MESSAGE: (
                        f'<a href="{ settings.URL_ROOT }elections/{ nominee_links[0].election.slug }'
                        f'/{ENDPOINT_DELETE_NOMINEE_LINKS}?'
                        f'{DELETE_NOMINEE_LINKS_REDIRECT_PATH_KEY}={request.path}"> '
                        'Click here delete the nominee links for the '
                        f'"{nominee_links[0].election.human_friendly_name}'
                        f' election before creating Nominee Links for this election.'
                        '</a>'
                    )
                })
        logger.info("[elections/election_page.py get_nominees()] time to vote")
        positions_list = {}
        votes_available = False
        if election_to_display.end_date is None or election_to_display.end_date <= get_current_date():
            votes_available = (
                VoterChoice.objects.all().filter(
                    selection__nominee_speech__nominee__election_id=election_to_display.id
                ).count() > 0
            )
            position_names = [position.position_name for position in NomineePosition.objects.all().filter(
                nominee_speech__nominee__election__slug=slug,
            ).order_by('position_index')]
            for position_name in position_names:
                if position_name not in positions_list:
                    positions_list[position_name] = {
                        "position_name": position_name,
                        "nominees": []
                    }
                    human_nominee_positions = NomineePosition.objects.all().filter(
                        position_name=position_name, nominee_speech__nominee__election__slug=slug,
                        nominee_speech__nominee__human_candidate=True
                    ).order_by('id')
                    if votes_available:
                        positions_list[position_name]["non_human_vote_info"] = ""
                        no_confidence_votes = VoterChoice.objects.all().filter(
                            selection__nominee_speech__nominee__full_name=NO_CONFIDENCE_NAME,
                            selection__position_name=position_name,
                            selection__nominee_speech__nominee__election_id=election_to_display.id
                        ).count()
                        skipped_votes = VoterChoice.objects.all().filter(
                            selection__nominee_speech__nominee__full_name=SKIPPED_VOTE,
                            selection__position_name=position_name,
                            selection__nominee_speech__nominee__election_id=election_to_display.id
                        ).count()
                        if no_confidence_votes > 0:
                            positions_list[position_name]['non_human_vote_info'] = (
                                f"{no_confidence_votes} vote{'s' if no_confidence_votes > 1 else ''} of No Confidence"
                            )
                            if skipped_votes > 0:
                                positions_list[position_name]['non_human_vote_info'] += " and "
                        if skipped_votes > 0:
                            positions_list[position_name]['non_human_vote_info'] += (
                                f"{skipped_votes} Skipped Vote{'s' if skipped_votes > 1 else ''}"
                            )
                        ordered_by_vote = {}
                        for human_nominee_position in human_nominee_positions:
                            vote_count = human_nominee_position.voterchoice_set.all().count()
                            if vote_count not in ordered_by_vote:
                                ordered_by_vote[vote_count] = [human_nominee_position]
                            else:
                                ordered_by_vote[vote_count].append(human_nominee_position)
                        order_count = list(ordered_by_vote.keys())
                        order_count.sort(reverse=True)
                        for vote_count in order_count:
                            nominees = ordered_by_vote[vote_count]
                            for nominee in nominees:
                                positions_list[position_name]['nominees'].append(nominee)
                    else:
                        for human_nominee_position in human_nominee_positions:
                            positions_list[position_name]['nominees'].append(human_nominee_position)
        context.update({
            ELECTION__HTML_NAME: election_to_display,
            POSITIONS_LIST_HTML__NAME: positions_list.values() if len(positions_list) > 0 else None,
            "vote_data_available": votes_available
        })
        return render(request, 'elections/election_page.html', context)
    else:
        logger.info("[elections/election_page.py get_nominees()] cant vote yet")
        return render(request, 'elections/election_page.html', context)
