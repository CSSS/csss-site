from elections.models import Election
from elections.views.Constants import SELECT_ELECTION_TYPE__NAME, \
    CURRENT_ELECTION_TYPES, SELECTED_ELECTION_TYPE__HTML_NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__ELECTION_TYPE


def create_context_for_election_type_html(context, election_type=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/webform_format/election_type.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the election_type.html
    election_type -- the user inputted election type
    """
    context.update({
        SELECT_ELECTION_TYPE__NAME: ELECTION_JSON_KEY__ELECTION_TYPE,
        CURRENT_ELECTION_TYPES: Election.election_type_choices,
        SELECTED_ELECTION_TYPE__HTML_NAME: election_type
    })
