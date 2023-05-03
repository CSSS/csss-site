import datetime

from csss.views_helper import DATE_FORMAT
from elections.views.Constants import INPUT_END_DATE__VALUE, INPUT_END_DATE__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__END_DATE


def create_context_for_election_end_date_html(context, election_end_date=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/webform_format/election_date.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the election_date.html
    election_end_date -- the user inputted election end date
    """
    context.update({
        INPUT_END_DATE__NAME: ELECTION_JSON_KEY__END_DATE,
        INPUT_END_DATE__VALUE: election_end_date.strftime(DATE_FORMAT) if type(election_end_date) is datetime.datetime
        else election_end_date,
    })
