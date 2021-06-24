import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from elections.models import Election
from elections.views.Constants import ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME, \
    ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY, SAVED_NOMINEE_LINKS, \
    NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS, SAVE_ELECTION__VALUE, UPDATE_EXISTING_ELECTION__NAME
from elections.views.create_context.nominee_links.create_nominee_links_context import \
    create_context_for_update_election_nominee_links_html
from elections.views.save_election.save_existing_election_obj_jformat import update_existing_election_obj_from_jformat
from elections.views.save_election.update_existing_nominee_links_from_jformat import \
    update_existing_nominee_links_from_jformat
from elections.views.update_election.nominee_links.display_selected_election_nominee_links import \
    display_selected_election_and_nominee_links
from elections.views.validators.validate_election_date import validate_webform_election_date_and_time
from elections.views.validators.validate_election_type import validate_election_type
from elections.views.validators.validate_link import validate_http_link
from elections.views.validators.validate_saved_nominee_links import validate_saved_nominee_links
from elections.views.validators.validate_user_command import validate_user_command

logger = logging.getLogger('csss_site')


def process_existing_election_and_nominee_links(request, context, slug):
    election = Election.objects.get(slug=slug)
    election_dict = parser.parse(request.POST.urlencode())
    if not (
            ELECTION_JSON_KEY__DATE in election_dict and ELECTION_JSON_WEBFORM_KEY__TIME in election_dict and
            ELECTION_JSON_KEY__ELECTION_TYPE in election_dict and ELECTION_JSON_KEY__WEBSURVEY in election_dict and
            SAVED_NOMINEE_LINKS in election_dict and NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS in election_dict):
        error_message = f"It seems that one of the following fields is missing" \
                        f" {ELECTION_JSON_KEY__DATE}, {ELECTION_JSON_WEBFORM_KEY__TIME}, " \
                        f"{ELECTION_JSON_KEY__ELECTION_TYPE}, " \
                        f"{ELECTION_JSON_KEY__WEBSURVEY}, {SAVED_NOMINEE_LINKS}, " \
                        f"{NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS}"
        logger.info(
            f"[elections/process_existing_election_and_nominee_links.py process_existing_election_and_nominee_links()] "
            f"{error_message}"
        )
        context.update(create_context_for_update_election_nominee_links_html(
            create_new_election=election is None, error_messages=[error_message], slug=slug
        ))
        return render(request, 'elections/update_election/update_election_nominee_links.html', context)
    election_dict[SAVED_NOMINEE_LINKS] = list(election_dict[SAVED_NOMINEE_LINKS].values())
    if not validate_user_command(request, create_new_election=False):
        error_message = "Unable to understand user command"
        logger.info(
            f"[elections/process_existing_election_and_nominee_links.py process_existing_election_and_nominee_links()] {error_message}"
        )
        context.update(create_context_for_update_election_nominee_links_html(
            create_new_election=election is None, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            draft_nominee_links=election_dict[SAVED_NOMINEE_LINKS],
            new_nominee_names=election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS], slug=slug
        ))
        return render(request, 'elections/update_election/update_election_nominee_links.html', context)

    success, error_message = validate_webform_election_date_and_time(
        election_dict[ELECTION_JSON_KEY__DATE], election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]
    )
    if not success:
        logger.info(
            f"[elections/process_existing_election_and_nominee_links.py process_existing_election_and_nominee_links()] "
            f"{error_message}"
        )
        context.update(create_context_for_update_election_nominee_links_html(
            create_new_election=election is None, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            draft_nominee_links=election_dict[SAVED_NOMINEE_LINKS],
            new_nominee_names=election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS], slug=slug)
        )
        return render(request, 'elections/update_election/update_election_nominee_links.html', context)

    success, error_message = validate_election_type(election_dict[ELECTION_JSON_KEY__ELECTION_TYPE])
    if not success:
        logger.info(
            f"[elections/process_existing_election_and_nominee_links.py process_existing_election_and_nominee_links()] "
            f"{error_message}"
        )
        context.update(create_context_for_update_election_nominee_links_html(
            create_new_election=election is None, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            draft_nominee_links=election_dict[SAVED_NOMINEE_LINKS],
            new_nominee_names=election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS], slug=slug)
        )
        return render(request, 'elections/update_election/update_election_nominee_links.html', context)

    success, error_message = validate_http_link(election_dict[ELECTION_JSON_KEY__WEBSURVEY], "websurvey")
    if not success:
        logger.info(
            f"[elections/process_existing_election_and_nominee_links.py process_existing_election_and_nominee_links()] "
            f"{error_message}"
        )
        context.update(create_context_for_update_election_nominee_links_html(
            create_new_election=election is None, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            draft_nominee_links=election_dict[SAVED_NOMINEE_LINKS],
            new_nominee_names=election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS], slug=slug)
        )
        return render(request, 'elections/update_election/update_election_nominee_links.html', context)
    success, error_message = validate_saved_nominee_links(election_dict[SAVED_NOMINEE_LINKS])
    if not success:
        logger.info(
            f"[elections/process_existing_election_and_nominee_links.py process_existing_election_and_nominee_links()] "
            f"{error_message}"
        )
        context.update(create_context_for_update_election_nominee_links_html(
            create_new_election=election is None, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            draft_nominee_links=election_dict[SAVED_NOMINEE_LINKS],
            new_nominee_names=election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS], slug=slug)
        )
        return render(request, 'elections/update_election/update_election_nominee_links.html', context)
    update_existing_election_obj_from_jformat(
        election, f"{election_dict[ELECTION_JSON_KEY__DATE]} {election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]}",
        election_dict[ELECTION_JSON_KEY__ELECTION_TYPE], election_dict[ELECTION_JSON_KEY__WEBSURVEY]
    )
    update_existing_nominee_links_from_jformat(election, election_dict[SAVED_NOMINEE_LINKS],
                                               election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS]
                                               )
    if request.POST[UPDATE_EXISTING_ELECTION__NAME] == SAVE_ELECTION__VALUE:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}')
    else:
        return display_selected_election_and_nominee_links(request, context, slug)
