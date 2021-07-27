import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from elections.views.Constants import ELECTION_JSON_WEBFORM_KEY__TIME, ELECTION_JSON_KEY__DATE, \
    ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__NOMINEES, CREATE_NEW_ELECTION__NAME, \
    SAVE_ELECTION__VALUE, ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_ID, ENDPOINT_MODIFY_VIA_WEBFORM
from elections.views.create_context.webform.create_webform_context import \
    create_webform_election_context_from_user_inputted_election_dict
from elections.views.save_election.save_new_election_from_jformat import save_new_election_from_jformat
from elections.views.utils.transform_webform_to_json import transform_full_election_webform_to_json
from elections.views.validators.validate_election_date import validate_webform_election_date_and_time
from elections.views.validators.validate_election_type import validate_election_type
from elections.views.validators.validate_link import validate_http_link
from elections.views.validators.validate_nominees_for_new_election import \
    validate_new_nominees_for_new_election
from elections.views.validators.validate_user_command import validate_user_command
from elections.views.validators.verify_that_all_relevant_election_webform_keys_exist import \
    verify_that_all_relevant_election_webform_keys_exist

logger = logging.getLogger('csss_site')


def process_new_inputted_webform_election(request, context):
    """
    Takes in the user's new election input and validates it before having it saved

    Keyword Argument:
    request -- the django request object that the new election is contained in
    context -- the dictionary that needs to be filled in with the user's input and the error message
     if there was an error

     Return
     either redirect user back to the page where they inputted the election info or direct them to the newly created
      election page
    """
    election_dict = transform_full_election_webform_to_json(parser.parse(request.POST.urlencode()))
    if not verify_that_all_relevant_election_webform_keys_exist(election_dict):
        error_message = f"Did not find all of the following necessary keys in input: " \
                        f"{ELECTION_JSON_KEY__DATE}, {ELECTION_JSON_WEBFORM_KEY__TIME}, " \
                        f"{ELECTION_JSON_KEY__ELECTION_TYPE}, {ELECTION_JSON_KEY__WEBSURVEY}, " \
                        f"{ELECTION_JSON_KEY__NOMINEES}, {CREATE_NEW_ELECTION__NAME}"
        logger.info(
            f"[elections/process_new_election_webform.py process_new_inputted_webform_election()] {error_message}"
        )
        context.update(create_webform_election_context_from_user_inputted_election_dict(error_message, election_dict))
        return render(request, 'elections/create_election/create_election_webform.html', context)

    if not validate_user_command(request):
        error_message = "Unable to understand user command"
        logger.info(
            f"[elections/process_new_election_webform.py process_new_inputted_webform_election()] {error_message}"
        )
        context.update(create_webform_election_context_from_user_inputted_election_dict(error_message, election_dict))
        return render(request, 'elections/create_election/create_election_webform.html', context)

    success, error_message = validate_http_link(election_dict[ELECTION_JSON_KEY__WEBSURVEY], "websurvey")
    if not success:
        logger.info(
            f"[elections/process_new_election_webform.py process_new_inputted_webform_election()] {error_message}"
        )
        context.update(create_webform_election_context_from_user_inputted_election_dict(error_message, election_dict))
        return render(request, 'elections/create_election/create_election_webform.html', context)

    success, error_message = validate_election_type(election_dict[ELECTION_JSON_KEY__ELECTION_TYPE])
    if not success:
        logger.info(
            f"[elections/process_new_election_webform.py process_new_inputted_webform_election()] {error_message}"
        )
        context.update(create_webform_election_context_from_user_inputted_election_dict(error_message, election_dict))
        return render(request, 'elections/create_election/create_election_webform.html', context)

    success, error_message = validate_webform_election_date_and_time(
        election_dict[ELECTION_JSON_KEY__DATE], election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]
    )
    if not success:
        logger.info(
            f"[elections/process_new_election_webform.py process_new_inputted_webform_election()] {error_message}"
        )
        context.update(create_webform_election_context_from_user_inputted_election_dict(error_message, election_dict))
        return render(request, 'elections/create_election/create_election_webform.html', context)

    success, error_message = validate_new_nominees_for_new_election(election_dict[ELECTION_JSON_KEY__NOMINEES])
    if not success:
        logger.info(
            f"[elections/process_new_election_webform.py process_new_inputted_webform_election()] {error_message}"
        )
        context.update(create_webform_election_context_from_user_inputted_election_dict(error_message, election_dict))
        return render(request, 'elections/create_election/create_election_webform.html', context)
    election = save_new_election_from_jformat(
        election_dict, json=False
    )
    if request.POST[CREATE_NEW_ELECTION__NAME] == SAVE_ELECTION__VALUE:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}')
    else:
        request.session[ELECTION_ID] = election.id
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{ENDPOINT_MODIFY_VIA_WEBFORM}')
