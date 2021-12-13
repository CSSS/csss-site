from elections.views.Constants import NOMINEE_DIV__NAME
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEES
from elections.views.create_context.nominee_links.utils.submission_buttons_html import \
    create_context_for_submission_buttons_html
from elections.views.create_context.webform_format.create_context_for_election_date_html import \
    create_context_for_election_date_html
from elections.views.create_context.webform_format.create_context_for_election_time_html import \
    create_context_for_election_time_html
from elections.views.create_context.webform_format.create_context_for_election_type_html import \
    create_context_for_election_type_html
from elections.views.create_context.webform_format.create_context_for_election_websurvey_html import \
    create_context_for_election_websurvey_html


def create_context_for_form__webform_html(context, election_date=None,
                                          election_time=None, election_type=None, websurvey_link=None,
                                          create_new_election=None):
    create_context_for_election_date_html(context, election_date=election_date)
    create_context_for_election_time_html(context, election_time=election_time)
    create_context_for_election_type_html(context, election_type=election_type)
    create_context_for_election_websurvey_html(context, websurvey_link=websurvey_link)
    create_context_for_submission_buttons_html(context, create_new_election=create_new_election)
    context[NOMINEE_DIV__NAME] = ELECTION_JSON_KEY__NOMINEES
