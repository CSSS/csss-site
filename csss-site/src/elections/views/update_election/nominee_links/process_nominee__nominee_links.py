from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.setup_logger import get_logger
from csss.views_helper import verify_user_input_has_all_required_fields
from elections.models import Election, NomineeSpeech, NomineePosition
from elections.views.Constants import ENDPOINT_CREATE_OR_UPDATE_NOMINEE_FOR_NOMINEE_VIA_PASSPHRASE__NOMINEE_LINK, \
    HTML_PASSPHRASE_GET_KEY, ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK, NOMINEE_LINK_ID
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOM_NAME, ELECTION_JSON_KEY__NOM_FACEBOOK, \
    ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOM_EMAIL, ELECTION_JSON_KEY__NOM_DISCORD, \
    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS
from elections.views.create_context.nominee_links.create_or_update_nominee. \
    create_context_for_create_or_update_nominee__nominee_links_html import \
    create_context_for_create_or_update_nominee__nominee_links_html
from elections.views.save_nominee.save_new_nominee_jformat import save_new_nominee_jformat
from elections.views.save_nominee.update_existing_nominees_jformat import update_existing_nominee_jformat
from elections.views.utils.webform_to_json.nominee_links.transform_nominee_links_webform_to_json import \
    transform_nominee_links_webform_to_json
from elections.views.validators.validate_existing_nominees__nominee_link import \
    validate_existing_nominee__nominee_link

logger = get_logger()


def process_nominee__nominee_links(request, context, nominee_link=None, passphrase=False):
    """
    Processes the user's input for modify the specified election

    Keyword Argument
    request -- django request object
    context -- the context dictionary
    nominee_link_id -- the ID for the nominee link that has to be modified

    Return
    render object that directs the user to the page for updating a nominee via nominee link
    """
    nominee_info = transform_nominee_links_webform_to_json(request)

    election_id = nominee_link.election.id
    fields = [
        ELECTION_JSON_KEY__NOM_NAME, ELECTION_JSON_KEY__NOM_FACEBOOK, ELECTION_JSON_KEY__NOM_LINKEDIN,
        ELECTION_JSON_KEY__NOM_EMAIL, ELECTION_JSON_KEY__NOM_DISCORD,
        ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS
    ]
    error_message = verify_user_input_has_all_required_fields(nominee_info, fields)
    if error_message != "":
        logger.info(
            f"[elections/process_nominee__nominee_links.py process_nominee__nominee_links()] "
            f"{error_message}"
        )
        create_context_for_create_or_update_nominee__nominee_links_html(
            context, nominee_link_id=nominee_link.id, error_messages=[error_message]
        )
        return render(
            request, 'elections/nominee_links/create_or_update_nominee/create_or_update_nominee__nominee_links.html',
            context
        )

    success, error_message = validate_existing_nominee__nominee_link(election_id, nominee_link.id, nominee_info)
    if not success:
        logger.info(
            f"[elections/process_nominee__nominee_links.py process_nominee__nominee_links()] "
            f"{error_message}"
        )
        create_context_for_create_or_update_nominee__nominee_links_html(
            context, nominee_link_id=nominee_link.id, error_messages=[error_message], nominee_info=nominee_info
        )
        return render(
            request, 'elections/nominee_links/create_or_update_nominee/create_or_update_nominee__nominee_links.html',
            context
        )
    if nominee_link.nominee is None:
        save_new_nominee_jformat(
            Election.objects.get(id=election_id), nominee_info[ELECTION_JSON_KEY__NOM_NAME],
            nominee_info[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS],
            nominee_info[ELECTION_JSON_KEY__NOM_FACEBOOK],
            nominee_info[ELECTION_JSON_KEY__NOM_LINKEDIN], nominee_info[ELECTION_JSON_KEY__NOM_EMAIL],
            nominee_info[ELECTION_JSON_KEY__NOM_DISCORD], nominee_link=nominee_link
        )
    else:
        position_ids, speech_ids = update_existing_nominee_jformat(nominee_link.nominee, nominee_info)

        current_nominee_position_ids_under_election = [
            speech.id for speech in NomineePosition.objects.all().filter(
                nominee_speech__nominee__nomineelink__id=nominee_link.id)
        ]
        position_ids_to_delete = [
            position_id for position_id in current_nominee_position_ids_under_election
            if position_id not in position_ids
        ]
        for position_id_to_delete in position_ids_to_delete:
            NomineePosition.objects.all().get(id=position_id_to_delete).delete()

        current_nominee_speech_ids_under_election = [
            speech.id for speech in NomineeSpeech.objects.all().filter(
                nominee__nomineelink__id=nominee_link.id)
        ]
        speech_ids_to_delete = [
            speech_id for speech_id in current_nominee_speech_ids_under_election
            if speech_id not in speech_ids
        ]
        for speech_id_to_delete in speech_ids_to_delete:
            NomineeSpeech.objects.all().get(id=speech_id_to_delete).delete()
    url = (
        f'{settings.URL_ROOT}elections/{ENDPOINT_CREATE_OR_UPDATE_NOMINEE_FOR_NOMINEE_VIA_PASSPHRASE__NOMINEE_LINK}?'
        f'{HTML_PASSPHRASE_GET_KEY}={nominee_link.passphrase}'
    ) if passphrase else (
        f'{settings.URL_ROOT}elections/{ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK}?'
        f'{NOMINEE_LINK_ID}={nominee_link.id}'
    )
    return HttpResponseRedirect(url)
