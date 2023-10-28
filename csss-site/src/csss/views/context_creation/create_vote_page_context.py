from csss.views.context_creation.error_htmls.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html
from elections.models import NomineePosition
from elections.views.Constants import ELECTION__HTML_NAME, NOMINEES_HTML__NAME


def create_vote_page_context(context, latest_election=None, error_messages=None, selected_positions=None,
                             can_vote=True, changes_pending=False):
    context['vote'] = can_vote
    context['changes_pending'] = changes_pending
    create_context_for_html_snippet_for_general_error_validations_html(context, error_messages=error_messages)
    if can_vote:
        context['show_nominees'] = True
        if latest_election is not None:
            positions = NomineePosition.objects.all().filter(
                nominee_speech__nominee__election__slug=latest_election.slug,
            ).order_by('position_index')
            context.update({
                ELECTION__HTML_NAME: latest_election,
                NOMINEES_HTML__NAME: positions,
            })
        if selected_positions:
            context['selected_nominee_positions'] = [
                int(nominee_position_id) for nominee_position_id in list(selected_positions.values())
            ]
    return context
