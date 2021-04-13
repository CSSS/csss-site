import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from elections.views.create_election.webform.process_new_election_webform import \
    create_webform_context_with_pre_populated_election_data
from elections.views.Constants import ELECTION_DATE_KEY, ELECTION_TIME_KEY, ELECTION_TYPE_KEY, \
    ELECTION_WEBSURVEY_LINK_KEY, ELECTION_NOMINEES_KEY, ELECTION_ID_KEY
from elections.views.extractors.get_existing_election_by_id import get_existing_election_by_id
from elections.views.save_election.save_existing_election_obj_jformat import update_existing_election_obj_from_jformat
from elections.views.save_nominee.save_new_or_update_existing_nominees_jformat import \
    save_new_or_update_existing_nominees_jformat
from elections.views.utils.transform_webform_to_json import transform_webform_to_json
from elections.views.validators.validate_nominees_for_existing_election_jformat import \
    validate_nominees_for_existing_election_jformat
from elections.views.validators.validate_election_date import validate_webform_election_date_and_time
from elections.views.validators.validate_election_type import validate_election_type

logger = logging.getLogger('csss_site')


def process_existing_election_information_from_webform(request, context):
    """
    Takes in the user's existing election input and validates it before having it saved

    Keyword Argument:
    request -- the django request object that the new election is contained in
    context -- the dictionary that needs to be filled in with the user's input and the error message
     if there was an error

     Return
     either redirect user back to the page where they inputted the election info or direct them to the election page
    """
    election_dict = transform_webform_to_json(parser.parse(request.POST.urlencode()))
    if not (ELECTION_DATE_KEY in election_dict and ELECTION_TIME_KEY in election_dict and
            ELECTION_TYPE_KEY in election_dict and ELECTION_WEBSURVEY_LINK_KEY in election_dict and
            ELECTION_ID_KEY in election_dict and ELECTION_NOMINEES_KEY in election_dict):
        error_message = f"Did not find all of the following necessary keys in input: " \
                        f"{ELECTION_DATE_KEY}, {ELECTION_TIME_KEY}, {ELECTION_TYPE_KEY}, " \
                        f"{ELECTION_WEBSURVEY_LINK_KEY}, {ELECTION_NOMINEES_KEY}, {ELECTION_ID_KEY}"
        logger.info(
            f"[elections/process_existing_election_webform.py process_existing_election_information_from_webform()]"
            f" {error_message}"
        )
        context.update(create_webform_context_with_pre_populated_election_data(error_message))
        return render(request, 'elections/update_election/update_election_webform.html', context)
    election = get_existing_election_by_id(election_dict[ELECTION_ID_KEY])
    if election is None:
        error_message = f"The Selected election for date {election_dict[ELECTION_DATE_KEY]} " \
                        f"does not exist"
        context.update(create_webform_context_with_pre_populated_election_data(error_message))
        return render(request, 'elections/update_election/update_election_webform.html', context)

    success, error_message = validate_election_type(election_dict[ELECTION_TYPE_KEY])
    if not success:
        context.update(create_webform_context_with_pre_populated_election_data(error_message, election_dict))
        return render(request, 'elections/update_election/update_election_webform.html', context)

    success, error_message = validate_webform_election_date_and_time(
        election_dict[ELECTION_DATE_KEY], election_dict[ELECTION_TIME_KEY]
    )
    if not success:
        context.update(create_webform_context_with_pre_populated_election_data(error_message, election_dict))
        return render(request, 'elections/update_election/update_election_webform.html', context)
    success, error_message = validate_nominees_for_existing_election_jformat(
        election.id, election_dict[ELECTION_NOMINEES_KEY]
    )
    if not success:
        context.update(create_webform_context_with_pre_populated_election_data(error_message, election_dict))
        return render(request, 'elections/update_election/update_election_webform.html', context)

    update_existing_election_obj_from_jformat(
        election, f"{election_dict[ELECTION_DATE_KEY]} {election_dict[ELECTION_TIME_KEY]}",
        election_dict[ELECTION_TYPE_KEY], election_dict[ELECTION_WEBSURVEY_LINK_KEY]
    )
    save_new_or_update_existing_nominees_jformat(election, election_dict)
    return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}/')
