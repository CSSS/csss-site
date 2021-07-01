import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from elections.views.Constants import ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__ELECTION_TYPE, \
    ELECTION_JSON_WEBFORM_KEY__TIME, ELECTION_JSON_KEY__DATE, CREATE_NEW_ELECTION__NAME, SAVE_ELECTION__VALUE, \
    NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS
from elections.views.create_context.nominee_links.create_nominee_links_context import \
    create_context_for_create_election_nominee_links_html
from elections.views.save_election.save_new_election_and_nominee_links import save_new_election_and_nominee_links
from elections.views.validators.validate_election_date import validate_webform_election_date_and_time
from elections.views.validators.validate_election_type import validate_election_type
from elections.views.validators.validate_link import validate_http_link
from elections.views.validators.validate_user_command import validate_user_command

logger = logging.getLogger('csss_site')


def process_new_election_and_nominee_links(request, context):
    election_dict = request.POST
    if not (ELECTION_JSON_KEY__WEBSURVEY in election_dict and ELECTION_JSON_KEY__ELECTION_TYPE and
            ELECTION_JSON_WEBFORM_KEY__TIME in election_dict and ELECTION_JSON_KEY__DATE in election_dict and
            NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS in election_dict):
        error_message = f"Did not find all of the following necessary keys in input: " \
                        f"{ELECTION_JSON_KEY__WEBSURVEY}, {ELECTION_JSON_KEY__ELECTION_TYPE}, " \
                        f"{ELECTION_JSON_WEBFORM_KEY__TIME}, {ELECTION_JSON_KEY__DATE}, " \
                        f"{NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS}"
        logger.info(
            "[elections/process_new_election_and_nominee_links.py process_new_election_and_nominee_links()]"
            f" {error_message}"
        )
        create_context_for_create_election_nominee_links_html(
            context, create_new_election=True, error_messages=[error_message]
        )
        return render(request, 'elections/create_election/create_election_nominee_links.html', context)
    if not validate_user_command(request):
        error_message = "Unable to understand user command"
        logger.info(
            "[elections/process_new_election_and_nominee_links.py process_new_election_and_nominee_links()]"
            f" {error_message}"
        )
        create_context_for_create_election_nominee_links_html(
            context, create_new_election=True, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominee_names=election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS]
        )
        return render(request, 'elections/create_election/create_election_nominee_links.html', context)

    success, error_message = validate_http_link(election_dict[ELECTION_JSON_KEY__WEBSURVEY], "websurvey")
    if not success:
        logger.info(
            "[elections/process_new_election_and_nominee_links.py process_new_election_and_nominee_links()]"
            f" {error_message}"
        )
        create_context_for_create_election_nominee_links_html(
            context, create_new_election=True, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominee_names=election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS]
        )
        return render(request, 'elections/create_election/create_election_nominee_links.html', context)

    success, error_message = validate_election_type(election_dict[ELECTION_JSON_KEY__ELECTION_TYPE])
    if not success:
        logger.info(
            "[elections/process_new_election_and_nominee_links.py process_new_election_and_nominee_links()]"
            f" {error_message}"
        )
        create_context_for_create_election_nominee_links_html(
            context, create_new_election=True, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominee_names=election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS]
        )
        return render(request, 'elections/create_election/create_election_nominee_links.html', context)

    success, error_message = validate_webform_election_date_and_time(
        election_dict[ELECTION_JSON_KEY__DATE], election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]
    )
    if not success:
        logger.info(
            "[elections/process_new_election_and_nominee_links.py process_new_election_and_nominee_links()]"
            f" {error_message}"
        )
        create_context_for_create_election_nominee_links_html(
            context, create_new_election=True, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominee_names=election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS]
        )
        return render(request, 'elections/create_election/create_election_nominee_links.html', context)
    election = save_new_election_and_nominee_links(election_dict)
    if request.POST[CREATE_NEW_ELECTION__NAME] == SAVE_ELECTION__VALUE:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}')
    else:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}')
        # return HttpResponseRedirect(
        #     f'{settings.URL_ROOT}elections/{election.slug}/{ENDPOINT_MODIFY_VIA_NOMINEE_LINKS}/'
        # )
