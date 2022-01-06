import datetime

from elections.views.Constants import INPUT_DATE__NAME, INPUT_DATE__VALUE, DATE_FORMAT
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__DATE


def create_context_for_election_date_html(context, election_date=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/webform_format/election_date.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the election_date.html
    election_date -- the user inputted election date
    """
    context.update({
        INPUT_DATE__NAME: ELECTION_JSON_KEY__DATE,
        INPUT_DATE__VALUE: election_date.strftime(DATE_FORMAT) if type(election_date) is datetime.datetime
        else election_date
    })
