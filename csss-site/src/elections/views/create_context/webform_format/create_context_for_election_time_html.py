import datetime

from elections.views.Constants import INPUT_TIME__NAME, INPUT_TIME__VALUE, \
    TIME_FORMAT
from elections.views.ElectionModelConstants import ELECTION_JSON_WEBFORM_KEY__TIME


def create_context_for_election_time_html(context, election_time=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/webform_format/election_time.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the election_time.html
    election_time -- the user inputted election time
    """
    context.update({
        INPUT_TIME__NAME: ELECTION_JSON_WEBFORM_KEY__TIME,
        INPUT_TIME__VALUE: election_time.strftime(TIME_FORMAT) if type(election_time) is datetime.datetime
        else election_time
    })
