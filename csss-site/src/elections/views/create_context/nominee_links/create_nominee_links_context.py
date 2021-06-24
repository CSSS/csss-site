import logging

from elections.models import Election
from elections.views.Constants import INPUT_DATE__NAME, ELECTION_JSON_KEY__DATE, INPUT_TIME__NAME, \
    ELECTION_JSON_WEBFORM_KEY__TIME, SELECT_ELECTION_TYPE__NAME, ELECTION_JSON_KEY__ELECTION_TYPE, \
    CURRENT_ELECTION_TYPES, INPUT_WEBSURVEY__NAME, ELECTION_JSON_KEY__WEBSURVEY, \
    NOMINEE_NAMES_FOR_NEW_NOMINEE_LINKS__HTML_NAME, NOMINEE_NAMES_FOR_NEW_NOMINEE_LINKS, NOMINEE_LINK_ID__HTML_NAME, \
    NOMINEE_LINK_ID, ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK__HTML_NAME, \
    ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK
from elections.views.create_context.submission_buttons_context import create_submission_buttons_context

logger = logging.getLogger('csss_site')


def create_webform_context(create_new_election=True):
    # NOMINEE_LINK_DIV__NAME: NOMINEE_LINKS
    pass


def create_nominee_links_context(create_new_election=True):
    context = {
        INPUT_DATE__NAME: ELECTION_JSON_KEY__DATE,
        INPUT_TIME__NAME: ELECTION_JSON_WEBFORM_KEY__TIME,
        SELECT_ELECTION_TYPE__NAME: ELECTION_JSON_KEY__ELECTION_TYPE,
        CURRENT_ELECTION_TYPES: Election.election_type_choices,
        INPUT_WEBSURVEY__NAME: ELECTION_JSON_KEY__WEBSURVEY,
        NOMINEE_NAMES_FOR_NEW_NOMINEE_LINKS__HTML_NAME: NOMINEE_NAMES_FOR_NEW_NOMINEE_LINKS,
        NOMINEE_LINK_ID__HTML_NAME: NOMINEE_LINK_ID,
        ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK__HTML_NAME:
            ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK
    }
    context.update(create_submission_buttons_context(create_new_election=create_new_election))

    logger.info("[elections/create_webform_context.py create_webform_nominee_links_context()] "
                f"created context of '{context}'")
    return context
