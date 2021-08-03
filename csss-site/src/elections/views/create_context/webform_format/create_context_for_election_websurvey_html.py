from elections.views.Constants import INPUT_WEBSURVEY__NAME, ELECTION_JSON_KEY__WEBSURVEY, CURRENT_WEBSURVEY_LINK


def create_context_for_election_websurvey_html(context, websurvey_link=None):
    context.update({
        INPUT_WEBSURVEY__NAME: ELECTION_JSON_KEY__WEBSURVEY,
        CURRENT_WEBSURVEY_LINK: websurvey_link,
    })
