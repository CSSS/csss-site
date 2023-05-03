from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.setup_logger import Loggers
from csss.views_helper import verify_user_input_has_all_required_fields
from elections.views.Constants import CREATE_NEW_ELECTION__NAME, SAVE_ELECTION__VALUE, \
    ENDPOINT_MODIFY_VIA_NOMINEE_LINKS, NEW_NOMINEE_SFUIDS_AND_DISCORD_IDS_FOR_NOMINEE_LINKS
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__ELECTION_TYPE, \
    ELECTION_JSON_WEBFORM_KEY__TIME, ELECTION_JSON_KEY__DATE, ELECTION_JSON_KEY__END_DATE
from elections.views.create_context.nominee_links.create_or_update_election. \
    create_context_for_create_election_nominee_links_html import \
    create_context_for_create_election_nominee_links_html
from elections.views.save_election.save_new_election_and_nominee_links import save_new_election_and_nominee_links
from elections.views.utils.webform_to_json.nominee_links.transform_election_nominee_links_webform_to_json import \
    transform_election_nominee_links_webform_to_json
from elections.views.validators.validate_election_date import validate_webform_election_date_and_time, \
    validate_webform_election_end_date
from elections.views.validators.validate_election_type import validate_election_type
from elections.views.validators.validate_election_uniqueness import validate_election_webform_format_uniqueness
from elections.views.validators.validate_link import validate_websurvey_link
from elections.views.validators.validate_new_nominee_sfuids_and_discord_ids import \
    validate_new_nominee_sfuids_and_discord_ids
from elections.views.validators.validate_user_command import validate_user_command


def process_new_election_and_nominee_links(request, context):
    """
    Takes in the user's new election and nominee link input and validates it before having it saved

    Keyword Argument:
    request -- the django request object that the new election is contained in
    context -- the dictionary that needs to be filled in with the user's input and the error message
     if there was an error

     Return
     either redirect user back to the page where they inputted the election info or direct them to the newly created
      election page along with nominee links
    """
    logger = Loggers.get_logger()
    election_dict = transform_election_nominee_links_webform_to_json(request)
    fields = [
        ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_WEBFORM_KEY__TIME,
        ELECTION_JSON_KEY__DATE, ELECTION_JSON_KEY__END_DATE, NEW_NOMINEE_SFUIDS_AND_DISCORD_IDS_FOR_NOMINEE_LINKS
    ]
    error_message = verify_user_input_has_all_required_fields(election_dict, fields=fields)
    if error_message != "":
        logger.info(
            "[elections/process_new_election_and_nominee_links.py process_new_election_and_nominee_links()]"
            f" {error_message}"
        )
        create_context_for_create_election_nominee_links_html(
            context, create_new_election=True, error_messages=[error_message]
        )
        return render(
            request, 'elections/nominee_links/create_or_update_election/create_election_nominee_links.html',
            context
        )
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
            election_end_date=election_dict[ELECTION_JSON_KEY__END_DATE],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominee_sfuids_and_discord_ids=election_dict[NEW_NOMINEE_SFUIDS_AND_DISCORD_IDS_FOR_NOMINEE_LINKS]
        )
        return render(
            request, 'elections/nominee_links/create_or_update_election/create_election_nominee_links.html',
            context
        )

    success, error_message = validate_websurvey_link(election_dict[ELECTION_JSON_KEY__WEBSURVEY])
    if not success:
        logger.info(
            "[elections/process_new_election_and_nominee_links.py process_new_election_and_nominee_links()]"
            f" {error_message}"
        )
        create_context_for_create_election_nominee_links_html(
            context, create_new_election=True, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_end_date=election_dict[ELECTION_JSON_KEY__END_DATE],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominee_sfuids_and_discord_ids=election_dict[NEW_NOMINEE_SFUIDS_AND_DISCORD_IDS_FOR_NOMINEE_LINKS]
        )
        return render(
            request, 'elections/nominee_links/create_or_update_election/create_election_nominee_links.html',
            context
        )

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
            election_end_date=election_dict[ELECTION_JSON_KEY__END_DATE],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominee_sfuids_and_discord_ids=election_dict[NEW_NOMINEE_SFUIDS_AND_DISCORD_IDS_FOR_NOMINEE_LINKS]
        )
        return render(
            request, 'elections/nominee_links/create_or_update_election/create_election_nominee_links.html',
            context
        )

    success, error_message = validate_webform_election_date_and_time(
        election_dict[ELECTION_JSON_KEY__DATE], election_dict[ELECTION_JSON_WEBFORM_KEY__TIME], new_election=True
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
            election_end_date=election_dict[ELECTION_JSON_KEY__END_DATE],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominee_sfuids_and_discord_ids=election_dict[NEW_NOMINEE_SFUIDS_AND_DISCORD_IDS_FOR_NOMINEE_LINKS]
        )
        return render(
            request, 'elections/nominee_links/create_or_update_election/create_election_nominee_links.html',
            context
        )
    success, error_message = validate_webform_election_end_date(
        election_dict[ELECTION_JSON_KEY__END_DATE],
        election_dict[ELECTION_JSON_KEY__DATE]
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
            election_end_date=election_dict[ELECTION_JSON_KEY__END_DATE],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominee_sfuids_and_discord_ids=election_dict[NEW_NOMINEE_SFUIDS_AND_DISCORD_IDS_FOR_NOMINEE_LINKS]
        )
        return render(
            request, 'elections/nominee_links/create_or_update_election/create_election_nominee_links.html',
            context
        )

    success, error_message = validate_election_webform_format_uniqueness(election_dict)
    if not success:
        logger.info(
            "[elections/process_new_election_and_nominee_links.py process_new_election_and_nominee_links()]"
            f" {error_message}"
        )
        create_context_for_create_election_nominee_links_html(
            context, create_new_election=True, error_messages=[error_message],
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_end_date=election_dict[ELECTION_JSON_KEY__END_DATE],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominee_sfuids_and_discord_ids=election_dict[NEW_NOMINEE_SFUIDS_AND_DISCORD_IDS_FOR_NOMINEE_LINKS]
        )
        return render(
            request, 'elections/nominee_links/create_or_update_election/create_election_nominee_links.html',
            context
        )
    success, error_message = validate_new_nominee_sfuids_and_discord_ids(
        election_dict[NEW_NOMINEE_SFUIDS_AND_DISCORD_IDS_FOR_NOMINEE_LINKS]
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
            election_end_date=election_dict[ELECTION_JSON_KEY__END_DATE],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominee_sfuids_and_discord_ids=election_dict[NEW_NOMINEE_SFUIDS_AND_DISCORD_IDS_FOR_NOMINEE_LINKS]
        )
        return render(
            request, 'elections/nominee_links/create_or_update_election/create_election_nominee_links.html',
            context
        )
    election = save_new_election_and_nominee_links(election_dict)
    if request.POST[CREATE_NEW_ELECTION__NAME] == SAVE_ELECTION__VALUE:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}')
    else:
        return HttpResponseRedirect(
            f'{settings.URL_ROOT}elections/{election.slug}/{ENDPOINT_MODIFY_VIA_NOMINEE_LINKS}'
        )
