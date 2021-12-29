from elections.views.Constants import INPUT_WEBSURVEY__NAME, CURRENT_WEBSURVEY_LINK
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__WEBSURVEY


def create_context_for_election_websurvey_html(context, websurvey_link=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/webform_format/election_websurvey.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the election_websurvey.html
    websurvey_link -- the user inputted election websurvey link
    """
    context.update({
        INPUT_WEBSURVEY__NAME: ELECTION_JSON_KEY__WEBSURVEY,
        CURRENT_WEBSURVEY_LINK: websurvey_link,
    })
