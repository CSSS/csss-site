from elections.views.Constants import NOMINEE_DIV__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEES
from elections.views.create_context.webform_format.create_context_for_election_date_html import \
    create_context_for_election_date_html
from elections.views.create_context.webform_format.create_context_for_election_time_html import \
    create_context_for_election_time_html
from elections.views.create_context.webform_format.create_context_for_election_type_html import \
    create_context_for_election_type_html
from elections.views.create_context.webform_format.create_context_for_election_websurvey_html import \
    create_context_for_election_websurvey_html
from elections.views.create_context.webform_format.submission_buttons_html import \
    create_context_for_submission_buttons_html


def create_context_for_form__webform_html(context, election_date=None,
                                          election_time=None, election_type=None, websurvey_link=None,
                                          new_webform_election=False):
    """
    Puts the included election info in the context dictionary

    Keyword Arguments
    context -- the context dictionary that has to be populated for the form__webform.html
    election_date -- the date of the election that the user inputted, otherwise None
    election_time -- the time of the election that the user inputted, otherwise None
    election_type -- the election type that the user inputted, otherwise None
    websurvey_link -- the websurvey link of the election that the user inputted, otherwise None
    new_webform_election -- bool to indicate if the election is a new webform election
    """
    create_context_for_election_date_html(context, election_date=election_date)
    create_context_for_election_time_html(context, election_time=election_time)
    create_context_for_election_type_html(context, election_type=election_type)
    create_context_for_election_websurvey_html(context, websurvey_link=websurvey_link)
    create_context_for_submission_buttons_html(context, create_new_election=new_webform_election)
    context[NOMINEE_DIV__NAME] = ELECTION_JSON_KEY__NOMINEES
