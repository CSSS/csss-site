from elections.models import Election
from elections.views.Constants import SELECT_ELECTION_TYPE__NAME, ELECTION_JSON_KEY__ELECTION_TYPE, \
    CURRENT_ELECTION_TYPES, SELECTED_ELECTION_TYPE__HTML_NAME


def create_context_for_election_type_html(context, election_type=None):
    context.update({
        SELECT_ELECTION_TYPE__NAME: ELECTION_JSON_KEY__ELECTION_TYPE,
        CURRENT_ELECTION_TYPES: Election.election_type_choices,
        SELECTED_ELECTION_TYPE__HTML_NAME: election_type
    })
