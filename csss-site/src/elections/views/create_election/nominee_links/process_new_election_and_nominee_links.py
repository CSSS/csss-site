import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.views_helper import ERROR_MESSAGES_KEY
from elections.views.Constants import ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__ELECTION_TYPE, \
    ELECTION_JSON_WEBFORM_KEY__TIME, ELECTION_JSON_KEY__DATE, CREATE_NEW_ELECTION__NAME, SAVE_ELECTION__VALUE, \
    ELECTION_ID, ENDPOINT_MODIFY_VIA_NOMINEE_LINKS
from elections.views.save_election.save_new_election_and_nominee_links import save_new_election_and_nominee_links
from elections.views.validators.validate_election_date import validate_webform_election_date_and_time
from elections.views.validators.validate_election_type import validate_election_type
from elections.views.validators.validate_link import validate_http_link
from elections.views.validators.validate_user_command import validate_user_command

logger = logging.getLogger('csss_site')


def process_new_election_and_nominee_links(request, context):
    election_dict = request.POST
    if not validate_user_command(request):
        error_message = "Unable to understand user command"
        logger.info(
            "[elections/process_new_election_and_nominee_links.py process_new_election_and_nominee_links()]"
            f" {error_message}"
        )
        context[ERROR_MESSAGES_KEY] = [error_message]
        return render(request, 'elections/nominee_links/create_election_nominee_links.html', context)

    success, error_message = validate_http_link(election_dict[ELECTION_JSON_KEY__WEBSURVEY], "websurvey")
    if not success:
        logger.info(
            "[elections/process_new_election_and_nominee_links.py process_new_election_and_nominee_links()]"
            f" {error_message}"
        )
        context[ERROR_MESSAGES_KEY] = [error_message]
        return render(request, 'elections/nominee_links/create_election_nominee_links.html', context)

    success, error_message = validate_election_type(election_dict[ELECTION_JSON_KEY__ELECTION_TYPE])
    if not success:
        logger.info(
            "[elections/process_new_election_and_nominee_links.py process_new_election_and_nominee_links()]"
            f" {error_message}"
        )
        context[ERROR_MESSAGES_KEY] = [error_message]
        return render(request, 'elections/nominee_links/create_election_nominee_links.html', context)

    success, error_message = validate_webform_election_date_and_time(
        election_dict[ELECTION_JSON_KEY__DATE], election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]
    )
    if not success:
        logger.info(
            "[elections/process_new_election_and_nominee_links.py process_new_election_and_nominee_links()]"
            f" {error_message}"
        )
        context[ERROR_MESSAGES_KEY] = [error_message]
        return render(request, 'elections/nominee_links/create_election_nominee_links.html', context)
    election = save_new_election_and_nominee_links(election_dict)
    if request.POST[CREATE_NEW_ELECTION__NAME] == SAVE_ELECTION__VALUE:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}')
    else:
        request.session[ELECTION_ID] = election.id
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{ENDPOINT_MODIFY_VIA_NOMINEE_LINKS}/')
