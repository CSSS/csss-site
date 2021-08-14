from elections.views.Constants import INPUT_WEBSURVEY__NAME, CURRENT_WEBSURVEY_LINK
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__WEBSURVEY


def create_context_for_election_websurvey_html(context, websurvey_link=None):
    context.update({
        INPUT_WEBSURVEY__NAME: ELECTION_JSON_KEY__WEBSURVEY,
        CURRENT_WEBSURVEY_LINK: websurvey_link,
    })
