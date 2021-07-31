import datetime

from elections.views.Constants import INPUT_TIME__NAME, ELECTION_JSON_WEBFORM_KEY__TIME, INPUT_TIME__VALUE, TIME_FORMAT


def create_context_for_election_time_html(context, election_time=None):
    context.update({
        INPUT_TIME__NAME: ELECTION_JSON_WEBFORM_KEY__TIME,
        INPUT_TIME__VALUE: election_time.strftime(TIME_FORMAT) if type(election_time) is datetime.datetime
        else election_time
    })
