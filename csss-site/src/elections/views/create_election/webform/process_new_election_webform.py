import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from elections.views.Constants import CREATE_NEW_ELECTION__NAME, \
    SAVE_ELECTION__VALUE, ENDPOINT_MODIFY_VIA_WEBFORM
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__DATE, ELECTION_JSON_KEY__ELECTION_TYPE, \
    ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__NOMINEES, ELECTION_JSON_WEBFORM_KEY__TIME
from elections.views.create_context.webform.create_context_for_create_election__webform_html import \
    create_context_for_create_election__webform_html
from elections.views.save_election.save_new_election_from_jformat import save_new_election_from_jformat
from elections.views.utils.transform_webform_to_json import transform_webform_to_json
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
    election_dict = transform_webform_to_json(parser.parse(request.POST.urlencode()))
    # election_dict = transform_webform_to_json(parser.parse(
    #     "csrfmiddlewaretoken=wovKZzoipz7z15KjcNWZPnL80b47XIr2kKCG21lu2286giLv7nJl7u4WqKTFRgGw&date=2021-12-08&time=00%3A34&election_type=by_election&websurvey=NONE&create_election=Save+and+Continue+Editing+Election&%5Bnominees%5D%5B0%5D%5Bname%5D=Courtenay+Huffman&%5Bnominees%5D%5B0%5D%5Bfacebook%5D=https%3A%2F%2Fwww.facebook.com%2Fcourtenay.huffman&%5Bnominees%5D%5B0%5D%5Blinkedin%5D=https%3A%2F%2Fwww.linkedin.com%2Fin%2Fwujohnw%2F&%5Bnominees%5D%5B0%5D%5Bemail%5D=rvanisck%40sfu.ca&%5Bnominees%5D%5B0%5D%5Bdiscord%5D=Jesus&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B2%5D%5Bposition_names%5D=President&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B2%5D%5Bposition_names%5D=Vice-President&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B2%5D%5Bspeech%5D=Courtenay+Huffman+Prez+and+VP+speech&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B4%5D%5Bposition_names%5D=Vice-President&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B4%5D%5Bposition_names%5D=Treasurer&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B4%5D%5Bspeech%5D=Courtenay+Huffman+Vp+and+Treasurer+speech&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B5%5D%5Bposition_names%5D=Director+of+Resources&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B5%5D%5Bposition_names%5D=Director+of+Archives&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B5%5D%5Bspeech%5D=Courtenay+Huffman+DoR+and+DoA+speech&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B6%5D%5Bposition_names%5D=Assistant+Director+of+Events&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B6%5D%5Bspeech%5D=Courtenay+Huffman+Assistant+DoE+speech&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B7%5D%5Bposition_names%5D=Director+of+Communications&%5Bnominees%5D%5B0%5D%5Bposition_names_and_speech_pairings%5D%5B7%5D%5Bspeech%5D=Courtenay+Huffman+DoC+speech&%5Bnominees%5D%5B1%5D%5Bname%5D=Daphne+Chong&%5Bnominees%5D%5B1%5D%5Bfacebook%5D=https%3A%2F%2Fwww.facebook.com%2Fprofile.php%3Fid%3D100009129288540&%5Bnominees%5D%5B1%5D%5Blinkedin%5D=https%3A%2F%2Fwww.linkedin.com%2Fin%2Fmitchell-gale-846153205%2F&%5Bnominees%5D%5B1%5D%5Bemail%5D=mgale%40sfu.ca&%5Bnominees%5D%5B1%5D%5Bdiscord%5D=Mitch%234755&%5Bnominees%5D%5B1%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bposition_names%5D=Vice-President&%5Bnominees%5D%5B1%5D%5Bposition_names_and_speech_pairings%5D%5B0%5D%5Bspeech%5D=Daphne+Chong+Vp+speech&%5Bnominees%5D%5B1%5D%5Bposition_names_and_speech_pairings%5D%5B1%5D%5Bposition_names%5D=President&%5Bnominees%5D%5B1%5D%5Bposition_names_and_speech_pairings%5D%5B1%5D%5Bspeech%5D=Daphne+Chong+Prez+speech"
    # ))

    if not verify_that_all_relevant_election_webform_keys_exist(election_dict):
        error_message = f"Did not find all of the following necessary keys in input: " \
                        f"{ELECTION_JSON_KEY__DATE}, {ELECTION_JSON_WEBFORM_KEY__TIME}, " \
                        f"{ELECTION_JSON_KEY__ELECTION_TYPE}, {ELECTION_JSON_KEY__WEBSURVEY}, " \
                        f"{ELECTION_JSON_KEY__NOMINEES}, {CREATE_NEW_ELECTION__NAME}"
        logger.info(
            f"[elections/process_new_election_webform.py process_new_inputted_webform_election()] {error_message}"
        )
        create_context_for_create_election__webform_html(
            context, error_messages=[error_message], election_dict=election_dict,
            webform_election=True, new_webform_election=True,
            include_id_for_nominee=False,
            draft_or_finalized_nominee_to_display=True
        )
        return render(request, 'elections/create_election/create_election__webform.html', context)

    if not validate_user_command(request):
        error_message = "Unable to understand user command"
        logger.info(
            f"[elections/process_new_election_webform.py process_new_inputted_webform_election()] {error_message}"
        )
        create_context_for_create_election__webform_html(
            context, error_messages=[error_message],
            webform_election=True, new_webform_election=True, include_id_for_nominee=False,
            draft_or_finalized_nominee_to_display=True,
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES]
        )
        return render(request, 'elections/create_election/create_election__webform.html', context)

    success, error_message = validate_http_link(election_dict[ELECTION_JSON_KEY__WEBSURVEY], "websurvey")
    if not success:
        logger.info(
            f"[elections/process_new_election_webform.py process_new_inputted_webform_election()] {error_message}"
        )
        create_context_for_create_election__webform_html(
            context, error_messages=[error_message],
            webform_election=True, new_webform_election=True, include_id_for_nominee=False,
            draft_or_finalized_nominee_to_display=True,
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES]
        )
        return render(request, 'elections/create_election/create_election__webform.html', context)

    success, error_message = validate_election_type(election_dict[ELECTION_JSON_KEY__ELECTION_TYPE])
    if not success:
        logger.info(
            f"[elections/process_new_election_webform.py process_new_inputted_webform_election()] {error_message}"
        )
        create_context_for_create_election__webform_html(
            context, error_messages=[error_message],
            webform_election=True, new_webform_election=True, include_id_for_nominee=False,
            draft_or_finalized_nominee_to_display=True,
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES]
        )
        return render(request, 'elections/create_election/create_election__webform.html', context)

    success, error_message = validate_webform_election_date_and_time(
        election_dict[ELECTION_JSON_KEY__DATE], election_dict[ELECTION_JSON_WEBFORM_KEY__TIME]
    )
    if not success:
        logger.info(
            f"[elections/process_new_election_webform.py process_new_inputted_webform_election()] {error_message}"
        )
        create_context_for_create_election__webform_html(
            context, error_messages=[error_message],
            webform_election=True, new_webform_election=True, include_id_for_nominee=False,
            draft_or_finalized_nominee_to_display=True,
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES]
        )
        return render(request, 'elections/create_election/create_election__webform.html', context)

    success, error_message = validate_new_nominees_for_new_election(election_dict[ELECTION_JSON_KEY__NOMINEES])
    if not success:
        logger.info(
            f"[elections/process_new_election_webform.py process_new_inputted_webform_election()] {error_message}"
        )
        create_context_for_create_election__webform_html(
            context, error_messages=[error_message],
            webform_election=True, new_webform_election=True, include_id_for_nominee=False,
            draft_or_finalized_nominee_to_display=True,
            election_date=election_dict[ELECTION_JSON_KEY__DATE],
            election_time=election_dict[ELECTION_JSON_WEBFORM_KEY__TIME],
            election_type=election_dict[ELECTION_JSON_KEY__ELECTION_TYPE],
            websurvey_link=election_dict[ELECTION_JSON_KEY__WEBSURVEY],
            nominees_info=election_dict[ELECTION_JSON_KEY__NOMINEES]
        )
        return render(request, 'elections/create_election/create_election__webform.html', context)
    election = save_new_election_from_jformat(
        election_dict, json=False
    )
    if request.POST[CREATE_NEW_ELECTION__NAME] == SAVE_ELECTION__VALUE:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}')
    else:
        return HttpResponseRedirect(f'{settings.URL_ROOT}elections/{election.slug}/{ENDPOINT_MODIFY_VIA_WEBFORM}')
