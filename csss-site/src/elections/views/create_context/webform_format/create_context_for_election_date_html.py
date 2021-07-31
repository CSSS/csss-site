import datetime

from elections.views.Constants import INPUT_DATE__NAME, ELECTION_JSON_KEY__DATE, INPUT_DATE__VALUE, DATE_FORMAT


def create_context_for_election_date_html(context, election_date=None):
    context.update({
        INPUT_DATE__NAME: ELECTION_JSON_KEY__DATE,
        INPUT_DATE__VALUE: election_date.strftime(DATE_FORMAT) if type(election_date) is datetime.datetime
        else election_date
    })
