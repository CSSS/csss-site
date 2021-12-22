import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from elections.views.Constants import UPDATE_EXISTING_ELECTION__NAME, SAVE_ELECTION__VALUE, \
    ENDPOINT_MODIFY_VIA_WEBFORM
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__DATE, ELECTION_JSON_WEBFORM_KEY__TIME, \
    ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__NOMINEES
from elections.views.create_context.webform.create_context_update_election__webform_html import \
    create_context_for_update_election__webform_html
from elections.views.save_election.save_existing_election_obj_jformat import update_existing_election_obj_from_jformat
from elections.views.save_nominee.save_new_or_update_existing_nominees_jformat import \
    save_new_or_update_existing_nominees_jformat
from elections.views.utils.transform_webform_to_json import transform_webform_to_json
from elections.views.validators.validate_election_date import validate_webform_election_date_and_time
from elections.views.validators.validate_election_type import validate_election_type
from elections.views.validators.validate_link import validate_http_link
from elections.views.validators.validate_nominees_for_existing_election_jformat import \
    validate_nominees_for_existing_election_jformat
from elections.views.validators.validate_user_command import validate_user_command
from elections.views.validators.verify_that_all_relevant_election_webform_keys_exist import \
    verify_that_all_relevant_election_webform_keys_exist

logger = logging.getLogger('csss_site')


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
    election_dict = transform_webform_to_json(parser.parse("csrfmiddlewaretoken=wAxSHHQRl0H4pA6ZVObiLf11siHLebjwSXBHSHBj4rnz7bireaLnDtxuWb5IJxin&date=2021-11-16&time=00%3A34&election_type=general_election&websurvey=http%3A%2F%2Fda_websurvey&update_election=Save+and+Continue+Editing+Election&%5Bnominees%5D%5B0%5D%5Bid%5D=206&%5Bnominees%5D%5B0%5D%5Bname%5D=Ali+Khamesy&%5Bnominees%5D%5B0%5D%5Bfacebook%5D=http%3A%2F%2FI_love_niggers&%5Bnominees%5D%5B0%5D%5Blinkedin%5D=http%3A%2F%2FJaceLinkeIn&%5Bnominees%5D%5B0%5D%5Bemail%5D=sup%40sfu.ca&%5Bnominees%5D%5B0%5D%5Bdiscord%5D=ali_ali&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bposition_names%5D=Treasurer_135&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bposition_names%5D=Director+of+Resources&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bposition_names%5D=SFSS+Council+Representative&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bspeech%5D=hey+buby&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bid%5D=115&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B1%5D%5Bposition_names%5D=Director+of+Events_131&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B1%5D%5Bspeech%5D=sup&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B1%5D%5Bid%5D=114&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B2%5D%5Bspeech%5D=niggas&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B3%5D%5Bposition_names%5D=President&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B3%5D%5Bposition_names%5D=Vice-President&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B3%5D%5Bposition_names%5D=Treasurer&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B3%5D%5Bspeech%5D=NONE&%5Bnominees%5D%5B1%5D%5Bid%5D=207&%5Bnominees%5D%5B1%5D%5Bname%5D=bubbaSparx&%5Bnominees%5D%5B1%5D%5Bfacebook%5D=NONE&%5Bnominees%5D%5B1%5D%5Blinkedin%5D=NONE&%5Bnominees%5D%5B1%5D%5Bemail%5D=NONE&%5Bnominees%5D%5B1%5D%5Bdiscord%5D=NONE&%5Bnominees%5D%5B1%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bposition_names%5D=Vice-President_134&%5Bnominees%5D%5B1%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bspeech%5D=boom+boom+cuck&%5Bnominees%5D%5B1%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bid%5D=116&%5Bnominees%5D%5B2%5D%5Bid%5D=205&%5Bnominees%5D%5B2%5D%5Bname%5D=Eric+Gao&%5Bnominees%5D%5B2%5D%5Bfacebook%5D=http%3A%2F%2FI+love+Facebook%21&%5Bnominees%5D%5B2%5D%5Blinkedin%5D=http%3A%2F%2FJaceLinkedIN&%5Bnominees%5D%5B2%5D%5Bemail%5D=rvanisck%40sfu.ca&%5Bnominees%5D%5B2%5D%5Bdiscord%5D=Jesus&%5Bnominees%5D%5B2%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bposition_names%5D=Director+of+Resources_128&%5Bnominees%5D%5B2%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bposition_names%5D=Director+of+Events_129&%5Bnominees%5D%5B2%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bspeech%5D=nigga+nigga&%5Bnominees%5D%5B2%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bid%5D=112&%5Bnominees%5D%5B2%5D%5Bposition_names_and_speech_pairings%5D%5B1%5D%5Bposition_names%5D=Assistant+Director+of+Events_130&%5Bnominees%5D%5B2%5D%5Bposition_names_and_speech_pairings%5D%5B1%5D%5Bspeech%5D=sup&%5Bnominees%5D%5B2%5D%5Bposition_names_and_speech_pairings%5D%5B1%5D%5Bid%5D=113&%5Bnominees%5D%5B3%5D%5Bname%5D=Arya+Tavakoli&%5Bnominees%5D%5B3%5D%5Bfacebook%5D=NONE&%5Bnominees%5D%5B3%5D%5Blinkedin%5D=NONE&%5Bnominees%5D%5B3%5D%5Bemail%5D=NONE&%5Bnominees%5D%5B3%5D%5Bdiscord%5D=NONE&%5Bnominees%5D%5B3%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bspeech%5D=NONE"))
    # election_dict = transform_webform_to_json(parser.parse(request.POST.urlencode()))
    if not verify_that_all_relevant_election_webform_keys_exist(election_dict):
        error_message = f"Did not find all of the following necessary keys in input: " \
                        f"{ELECTION_JSON_KEY__DATE}, {ELECTION_JSON_WEBFORM_KEY__TIME}, " \
                        f"{ELECTION_JSON_KEY__ELECTION_TYPE}, " \
                        f"{ELECTION_JSON_KEY__WEBSURVEY}, {ELECTION_JSON_KEY__NOMINEES}"
        logger.info(
            f"[elections/process_existing_election_webform.py process_existing_election_information_from_webform()]"
            f" {error_message}"
        )
        create_context_for_update_election__webform_html(
            context, error_messages=[error_message], election_dict=election_dict,
            process_update_to_existing_election=True
        )
        return render(request, 'elections/update_election/update_election__webform.html', context)

    if not validate_user_command(request, create_new_election=False):
        error_message = "Unable to understand user command"
        logger.info(
            f"[elections/process_existing_election_webform.py process_existing_election_information_from_webform()] "
            f"{error_message, election_dict}"
        )
        create_context_for_update_election__webform_html(
            context, error_messages=[error_message], election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            webform_election=True, new_webform_election=False,
            include_id_for_nominee=True, draft_or_finalized_nominee_to_display=True,
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES],
            process_update_to_existing_election=True
        )
        return render(request, 'elections/update_election/update_election__webform.html', context)

    success, error_message = validate_election_type(election_dict[ELECTION_JSON_KEY__ELECTION_TYPE])
    if not success:
        logger.info(
            f"[elections/process_existing_election_webform.py process_existing_election_information_from_webform()]"
            f" {error_message}"
        )
        create_context_for_update_election__webform_html(
            context, error_messages=[error_message], election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            webform_election=True, new_webform_election=False,
            include_id_for_nominee=True, draft_or_finalized_nominee_to_display=True,
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES],
            process_update_to_existing_election=True
        )
        return render(request, 'elections/update_election/update_election__webform.html', context)

    success, error_message = validate_http_link(election_dict[ELECTION_JSON_KEY__WEBSURVEY], "websurvey")
    if not success:
        logger.info(
            f"[elections/process_existing_election_webform.py process_existing_election_information_from_webform()] "
            f"{error_message}"
        )
        create_context_for_update_election__webform_html(
            context, error_messages=[error_message], election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            webform_election=True, new_webform_election=False,
            include_id_for_nominee=True, draft_or_finalized_nominee_to_display=True,
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES],
            process_update_to_existing_election=True
        )
        return render(request, 'elections/update_election/update_election__webform.html', context)

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
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            webform_election=True, new_webform_election=False,
            include_id_for_nominee=True, draft_or_finalized_nominee_to_display=True,
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES],
            process_update_to_existing_election=True
        )
        return render(request, 'elections/update_election/update_election__webform.html', context)
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
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            webform_election=True, new_webform_election=False,
            include_id_for_nominee=True, draft_or_finalized_nominee_to_display=True,
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES],
            process_update_to_existing_election=True
        )
        return render(request, 'elections/update_election/update_election__webform.html', context)

    update_existing_election_obj_from_jformat(
        election, f"{election_dict[ELECTION_JSON_KEY__DATE]} {election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]}",
        election_dict[ELECTION_JSON_KEY__ELECTION_TYPE], election_dict[ELECTION_JSON_KEY__WEBSURVEY]
    )
    save_new_or_update_existing_nominees_jformat(election, election_dict)
    if request.POST[UPDATE_EXISTING_ELECTION__NAME] == SAVE_ELECTION__VALUE:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}/')
    else:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}/{ENDPOINT_MODIFY_VIA_WEBFORM}')
