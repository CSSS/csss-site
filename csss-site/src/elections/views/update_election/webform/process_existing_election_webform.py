from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from csss.setup_logger import Loggers
from csss.views_helper import verify_user_input_has_all_required_fields
from elections.views.Constants import UPDATE_EXISTING_ELECTION__NAME, SAVE_ELECTION__VALUE, \
    ENDPOINT_MODIFY_VIA_WEBFORM
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME, \
    ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__NOMINEES, \
    ELECTION_JSON_KEY__END_DATE
from elections.views.create_context.webform.create_context_for_update_election__webform_html import \
    create_context_for_update_election__webform_html
from elections.views.save_election.save_existing_election_obj_jformat import update_existing_election_obj_from_jformat
from elections.views.save_nominee.save_new_or_update_existing_nominees_jformat import \
    save_new_or_update_existing_nominees_jformat
from elections.views.utils.transform_webform_to_json import transform_webform_to_json
from elections.views.validators.validate_election_date import validate_webform_election_date_and_time, \
    validate_webform_election_end_date
from elections.views.validators.validate_election_type import validate_election_type
from elections.views.validators.validate_election_uniqueness import validate_election_webform_format_uniqueness
from elections.views.validators.validate_link import validate_websurvey_link
from elections.views.validators.validate_nominees_for_existing_election_jformat import \
    validate_nominees_for_existing_election_jformat
from elections.views.validators.validate_user_command import validate_user_command


def process_existing_election_information_from_webform(request, election, context):
    """
    Takes in the user's existing election input and validates it before having it saved

    Keyword Argument:
    request -- the django request object that the new election is contained in
    election -- the election object for the election that has to be displayed
    context -- the dictionary that needs to be filled in with the user's input and the error message
     if there was an error

     Return
     either redirect user back to the page where they inputted the election info or direct them to the election page
    """
    logger = Loggers.get_logger()
    election_dict = transform_webform_to_json(parser.parse(request.POST.urlencode()))
    fields = [
        ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME, ELECTION_JSON_KEY__END_DATE,
        ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__NOMINEES
    ]
    error_message = verify_user_input_has_all_required_fields(election_dict, fields=fields)
    if error_message != "":
        logger.info(
            f"[elections/process_existing_election_webform.py process_existing_election_information_from_webform()]"
            f" {error_message}"
        )
        create_context_for_update_election__webform_html(
            context, error_messages=[error_message], election_dict=election_dict,
            create_or_update_webform_election=True
        )
        return render(request, 'elections/webform/update_election__webform.html', context)

    if not validate_user_command(request, create_new_election=False):
        error_message = "Unable to understand user command"
        logger.info(
            f"[elections/process_existing_election_webform.py process_existing_election_information_from_webform()] "
            f"{error_message}"
        )
        create_context_for_update_election__webform_html(
            context, error_messages=[error_message], election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_end_date=election_dict[ELECTION_JSON_KEY__END_DATE],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES],
            create_or_update_webform_election=True
        )
        return render(request, 'elections/webform/update_election__webform.html', context)

    success, error_message = validate_election_type(election_dict[ELECTION_JSON_KEY__ELECTION_TYPE])
    if not success:
        logger.info(
            f"[elections/process_existing_election_webform.py process_existing_election_information_from_webform()]"
            f" {error_message}"
        )
        create_context_for_update_election__webform_html(
            context, error_messages=[error_message], election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_end_date=election_dict[ELECTION_JSON_KEY__END_DATE],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES],
            create_or_update_webform_election=True
        )
        return render(request, 'elections/webform/update_election__webform.html', context)

    success, error_message = validate_websurvey_link(election_dict[ELECTION_JSON_KEY__WEBSURVEY])
    if not success:
        logger.info(
            f"[elections/process_existing_election_webform.py process_existing_election_information_from_webform()] "
            f"{error_message}"
        )
        create_context_for_update_election__webform_html(
            context, error_messages=[error_message], election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_end_date=election_dict[ELECTION_JSON_KEY__END_DATE],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES],
            create_or_update_webform_election=True
        )
        return render(request, 'elections/webform/update_election__webform.html', context)

    success, error_message = validate_webform_election_date_and_time(
        election_dict[ELECTION_JSON_KEY__DATE], election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]
    )
    if not success:
        logger.info(
            f"[elections/process_existing_election_webform.py process_existing_election_information_from_webform()]"
            f" {error_message}"
        )
        create_context_for_update_election__webform_html(
            context, error_messages=[error_message], election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_end_date=election_dict[ELECTION_JSON_KEY__END_DATE],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES],
            create_or_update_webform_election=True
        )
        return render(request, 'elections/webform/update_election__webform.html', context)

    success, error_message = validate_webform_election_end_date(
        election_dict[ELECTION_JSON_KEY__END_DATE],
        election_dict[ELECTION_JSON_KEY__DATE]
    )
    if not success:
        logger.info(
            f"[elections/process_existing_election_webform.py process_existing_election_information_from_webform()]"
            f" {error_message}"
        )
        create_context_for_update_election__webform_html(
            context, error_messages=[error_message], election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_end_date=election_dict[ELECTION_JSON_KEY__END_DATE],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES],
            create_or_update_webform_election=True
        )
        return render(request, 'elections/webform/update_election__webform.html', context)
    success, error_message = validate_election_webform_format_uniqueness(election_dict, election_obj=election)
    if not success:
        logger.info(
            f"[elections/process_existing_election_webform.py process_existing_election_information_from_webform()]"
            f" {error_message}"
        )
        create_context_for_update_election__webform_html(
            context, error_messages=[error_message], election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_end_date=election_dict[ELECTION_JSON_KEY__END_DATE],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES],
            create_or_update_webform_election=True
        )
        return render(request, 'elections/webform/update_election__webform.html', context)

    success, error_message = validate_nominees_for_existing_election_jformat(
        election.id, election_dict[ELECTION_JSON_KEY__NOMINEES]
    )
    if not success:
        logger.info(
            f"[elections/process_existing_election_webform.py process_existing_election_information_from_webform()]"
            f" {error_message}"
        )
        create_context_for_update_election__webform_html(
            context, error_messages=[error_message], election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_end_date=election_dict[ELECTION_JSON_KEY__END_DATE],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES],
            create_or_update_webform_election=True
        )
        return render(request, 'elections/webform/update_election__webform.html', context)

    update_existing_election_obj_from_jformat(
        election, f"{election_dict[ELECTION_JSON_KEY__DATE]} {election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]}",
        election_dict[ELECTION_JSON_KEY__END_DATE],
        election_dict[ELECTION_JSON_KEY__ELECTION_TYPE], election_dict[ELECTION_JSON_KEY__WEBSURVEY]
    )
    save_new_or_update_existing_nominees_jformat(election, election_dict)
    if request.POST[UPDATE_EXISTING_ELECTION__NAME] == SAVE_ELECTION__VALUE:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}/')
    else:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}/{ENDPOINT_MODIFY_VIA_WEBFORM}')
