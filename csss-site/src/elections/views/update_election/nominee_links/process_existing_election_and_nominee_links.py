import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from elections.views.Constants import SAVED_NOMINEE_LINKS, \
    NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS, SAVE_ELECTION__VALUE, UPDATE_EXISTING_ELECTION__NAME, \
    ENDPOINT_MODIFY_VIA_NOMINEE_LINKS
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME, \
    ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY
from elections.views.create_context.nominee_links.create_or_update_election.create_context_for_update_election_nominee_links_html import \
    create_context_for_update_election_nominee_links_html
from elections.views.save_election.save_existing_election_obj_jformat import update_existing_election_obj_from_jformat
from elections.views.save_election.save_new_nominee_links_from_jformat import save_new_nominee_links_from_jformat
from elections.views.save_election.update_existing_nominee_links_from_jformat import \
    update_existing_nominee_links_from_jformat
from elections.views.utils.webform_to_json.nominee_links.transform_election_nominee_links_webform_to_json import \
    transform_election_nominee_links_webform_to_json
from elections.views.validators.validate_election_date import validate_webform_election_date_and_time
from elections.views.validators.validate_election_type import validate_election_type
from elections.views.validators.validate_link import validate_websurvey_link
from elections.views.validators.validate_saved_nominee_links import validate_saved_nominee_links
from elections.views.validators.validate_user_command import validate_user_command
from elections.views.validators.validate_user_input_has_required_fields import \
    verify_user_input_has_all_required_fields

logger = logging.getLogger('csss_site')


def process_existing_election_and_nominee_links(request, election, context):
    """
    Processes the user's input for modify the specified election and its nominee links

    Keyword Argument
    request -- django request object
    election -- the election object for the election that has to be displayed
    context -- the context dictionary

    Return
    render object that directs the user to the page for updating the election and its nominee links
    """
    election_dict = transform_election_nominee_links_webform_to_json(request)
    fields = [
        ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME, ELECTION_JSON_KEY__ELECTION_TYPE,
        ELECTION_JSON_KEY__WEBSURVEY, [SAVED_NOMINEE_LINKS, NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS]
    ]
    error_message = verify_user_input_has_all_required_fields(election_dict, fields)
    if error_message != "":
        logger.info(
            "[elections/process_existing_election_and_nominee_links.py"
            f" process_existing_election_and_nominee_links()] {error_message}"
        )
        create_context_for_update_election_nominee_links_html(
            context, create_new_election=election is None, error_messages=[error_message], election_obj=election
        )
        return render(
            request,
            'elections/nominee_links/create_or_update_election/update_election_nominee_links.html',
            context
        )

    if not validate_user_command(request, create_new_election=False):
        error_message = "Unable to understand user command"
        logger.info(
            "[elections/process_existing_election_and_nominee_links.py"
            f" process_existing_election_and_nominee_links()] {error_message}"
        )
        create_context_for_update_election_nominee_links_html(
            context, create_new_election=election is None, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            draft_nominee_links=election_dict[SAVED_NOMINEE_LINKS]
            if SAVED_NOMINEE_LINKS in election_dict else None,
            new_nominee_names=election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS]
            if NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS in election_dict else None,
            election_obj=election
        )
        return render(
            request,
            'elections/nominee_links/create_or_update_election/update_election_nominee_links.html',
            context
        )

    success, error_message = validate_webform_election_date_and_time(
        election_dict[ELECTION_JSON_KEY__DATE], election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]
    )
    if not success:
        logger.info(
            "[elections/process_existing_election_and_nominee_links.py"
            f" process_existing_election_and_nominee_links()] {error_message}"
        )
        create_context_for_update_election_nominee_links_html(
            context, create_new_election=election is None, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            draft_nominee_links=election_dict[SAVED_NOMINEE_LINKS]
            if SAVED_NOMINEE_LINKS in election_dict else None,
            new_nominee_names=election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS]
            if NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS in election_dict else None,
            election_obj=election
        )
        return render(
            request,
            'elections/nominee_links/create_or_update_election/update_election_nominee_links.html',
            context
        )

    success, error_message = validate_election_type(election_dict[ELECTION_JSON_KEY__ELECTION_TYPE])
    if not success:
        logger.info(
            "[elections/process_existing_election_and_nominee_links.py"
            f" process_existing_election_and_nominee_links()] {error_message}"
        )
        create_context_for_update_election_nominee_links_html(
            context, create_new_election=election is None, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            draft_nominee_links=election_dict[SAVED_NOMINEE_LINKS]
            if SAVED_NOMINEE_LINKS in election_dict else None,
            new_nominee_names=election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS]
            if NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS in election_dict else None,
            election_obj=election
        )
        return render(
            request,
            'elections/nominee_links/create_or_update_election/update_election_nominee_links.html',
            context
        )

    success, error_message = validate_websurvey_link(election_dict[ELECTION_JSON_KEY__WEBSURVEY])
    if not success:
        logger.info(
            "[elections/process_existing_election_and_nominee_links.py"
            f" process_existing_election_and_nominee_links()] {error_message}"
        )
        create_context_for_update_election_nominee_links_html(
            context, create_new_election=election is None, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            draft_nominee_links=election_dict[SAVED_NOMINEE_LINKS]
            if SAVED_NOMINEE_LINKS in election_dict else None,
            new_nominee_names=election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS]
            if NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS in election_dict else None,
            election_obj=election
        )

        return render(
            request,
            'elections/nominee_links/create_or_update_election/update_election_nominee_links.html',
            context
        )
    if SAVED_NOMINEE_LINKS in election_dict:
        success, error_message = validate_saved_nominee_links(election_dict[SAVED_NOMINEE_LINKS])
        if not success:
            logger.info(
                "[elections/process_existing_election_and_nominee_links.py"
                f" process_existing_election_and_nominee_links()] {error_message}"
            )
            create_context_for_update_election_nominee_links_html(
                context, create_new_election=election is None, error_messages=[error_message],
                election_date=election_dict[ELECTION_JSON_KEY__DATE],
                election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
                election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
                websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
                draft_nominee_links=election_dict[SAVED_NOMINEE_LINKS],
                new_nominee_names=election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS]
                if NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS in election_dict else None,
                election_obj=election
            )
            return render(
                request,
                'elections/nominee_links/create_or_update_election/update_election_nominee_links.html',
                context
            )
    update_existing_election_obj_from_jformat(
        election, f"{election_dict[ELECTION_JSON_KEY__DATE]} {election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]}",
        election_dict[ELECTION_JSON_KEY__ELECTION_TYPE], election_dict[ELECTION_JSON_KEY__WEBSURVEY]
    )
    update_existing_nominee_links_from_jformat(
        election_dict[SAVED_NOMINEE_LINKS] if SAVED_NOMINEE_LINKS in election_dict else None
    )
    save_new_nominee_links_from_jformat(
        election,
        election_dict[NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS]
        if NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS in election_dict else None
    )
    if request.POST[UPDATE_EXISTING_ELECTION__NAME] == SAVE_ELECTION__VALUE:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}')
    else:
        return HttpResponseRedirect(
            f'{settings.URL_ROOT}elections/{election.slug}/{ENDPOINT_MODIFY_VIA_NOMINEE_LINKS}'
        )
