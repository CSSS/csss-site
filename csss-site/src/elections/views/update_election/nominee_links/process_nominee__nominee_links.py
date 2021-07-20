import logging

from django.shortcuts import render
from querystring_parser import parser

from elections.models import Nominee, NomineeLink, Election, NomineeSpeech, NomineePosition
from elections.views.Constants import ELECTION_JSON_KEY__NOM_NAME, ELECTION_JSON_KEY__NOM_FACEBOOK, \
    ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOM_EMAIL, ELECTION_JSON_KEY__NOM_DISCORD, \
    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, ID_KEY
from elections.views.create_context.nominee_links.create_nominee_links_context_v2 import \
    create_context_for_update_nominee_html
from elections.views.save_nominee.save_new_nominee_jformat import save_new_nominee_jformat
from elections.views.save_nominee.update_existing_nominees_jformat import update_existing_nominee_jformat
from elections.views.update_election.nominee_links.display_selected_nominee_nominee_links import \
    display_current_nominee_link_election
from elections.views.utils.transform_webform_to_json_v2 import transform_nominee_links_webform_to_json
from elections.views.validators.validate_existing_nominee_jformat import validate_existing_nominee_jformat

logger = logging.getLogger('csss_site')


def process_nominee__nominee_links(request, context, nominee_link_id):
    nominee_info = transform_nominee_links_webform_to_json(parser.parse(request.POST.urlencode()))

    nominee_links = NomineeLink.objects.all().filter(id=nominee_link_id)
    if len(nominee_links) != 1:
        error_message = "Invalid Nominee Link ID"
        logger.info(
            f"[elections/process_nominee__nominee_links.py process_nominee__nominee_links()] "
            f"{error_message}"
        )
        context.update(
            create_context_for_update_nominee_html(nominee_link_id=nominee_link_id, error_messages=[error_message])
            )
        return render(request, 'elections/update_nominee/update_nominee.html', context)
    nominee_link = nominee_links[0]
    election_id = nominee_link.election.id
    if not (ELECTION_JSON_KEY__NOM_NAME in nominee_info and ELECTION_JSON_KEY__NOM_FACEBOOK in nominee_info
            and ELECTION_JSON_KEY__NOM_LINKEDIN in nominee_info and ELECTION_JSON_KEY__NOM_EMAIL in nominee_info
            and ELECTION_JSON_KEY__NOM_DISCORD in nominee_info
            and ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS in nominee_info):
        error_message = f"It seems that one of the nominees is missing one of the following fields:" \
                        f" {ELECTION_JSON_KEY__NOM_NAME}, {ELECTION_JSON_KEY__NOM_FACEBOOK}, " \
                        f"{ELECTION_JSON_KEY__NOM_LINKEDIN}, " \
                        f"{ELECTION_JSON_KEY__NOM_EMAIL}, {ELECTION_JSON_KEY__NOM_DISCORD}, " \
                        f"{ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS}"
        logger.info(
            f"[elections/process_nominee__nominee_links.py process_nominee__nominee_links()] "
            f"{error_message}"
        )
        context.update(
            create_context_for_update_nominee_html(nominee_link_id=nominee_link_id, error_messages=[error_message])
            )
        return render(request, 'elections/update_nominee/update_nominee.html', context)
    if ID_KEY in nominee_info:
        if f"{nominee_info[ID_KEY]}".isdigit():
            matching_nominees_under_specified_election = Nominee.objects.all().filter(
                id=int(nominee_info[ID_KEY]), nomineelink__id=nominee_link_id
            )
            if len(matching_nominees_under_specified_election) == 0:
                error_message = f"Invalid nominee id of {int(nominee_info[ID_KEY])} detected"
                logger.info(
                    f"[elections/process_nominee__nominee_links.py process_nominee__nominee_links()] "
                    f"{error_message}"
                )
                context.update(create_context_for_update_nominee_html(nominee_link_id=nominee_link_id,
                                                                      error_messages=[error_message])
                               )
                return render(request, 'elections/update_nominee/update_nominee.html', context)
        else:
            error_message = f"Invalid type detected for nominee id of {nominee_info[ID_KEY]}"
            logger.info(
                f"[elections/process_nominee__nominee_links.py process_nominee__nominee_links()] "
                f"{error_message}"
            )
            context.update(
                create_context_for_update_nominee_html(nominee_link_id=nominee_link_id, error_messages=[error_message])
                )
            return render(request, 'elections/update_nominee/update_nominee.html', context)
    nominee_names_so_far = [nominee.name for nominee in Nominee.objects.all().filter(
        election_id=election_id).exclude(nomineelink__id=nominee_link_id)
    ]
    speech_ids_so_far = []
    position_ids_so_far = []
    success, error_message = validate_existing_nominee_jformat(
        nominee_names_so_far, speech_ids_so_far, position_ids_so_far,
        nominee_info[ELECTION_JSON_KEY__NOM_NAME], nominee_info[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS],
        nominee_info[ELECTION_JSON_KEY__NOM_FACEBOOK], nominee_info[ELECTION_JSON_KEY__NOM_LINKEDIN],
        nominee_info[ELECTION_JSON_KEY__NOM_EMAIL], nominee_info[ELECTION_JSON_KEY__NOM_DISCORD], election_id)
    if not success:
        logger.info(
            f"[elections/process_nominee__nominee_links.py process_nominee__nominee_links()] "
            f"{error_message}"
        )
        context.update(
            create_context_for_update_nominee_html(nominee_link_id=nominee_link_id, error_messages=[error_message],
                                                   nominee_info=nominee_info)
            )
        return render(request, 'elections/update_nominee/update_nominee.html', context)
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

        current_nominee_speech_ids_under_election = [
            speech.id for speech in NomineeSpeech.objects.all().filter(
                nominee__nomineelink__id=nominee_link_id)
        ]
        speech_ids_to_delete = [
            speech_id for speech_id in current_nominee_speech_ids_under_election
            if speech_id not in speech_ids
        ]
        for speech_id_to_delete in speech_ids_to_delete:
            NomineeSpeech.objects.all().get(id=speech_id_to_delete).delete()

        current_nominee_position_ids_under_election = [
            speech.id for speech in NomineePosition.objects.all().filter(
                nominee_speech__nominee__nomineelink__id=nominee_link_id)
        ]
        position_ids_to_delete = [
            position_id for position_id in current_nominee_position_ids_under_election
            if position_id not in position_ids
        ]
        for position_id_to_delete in position_ids_to_delete:
            NomineePosition.objects.all().get(id=position_id_to_delete).delete()
    return display_current_nominee_link_election(request, context, nominee_link_id)
