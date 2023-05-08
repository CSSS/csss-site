from csss.setup_logger import Loggers
from elections.models import Nominee, NomineeSpeech, NomineePosition
from elections.views.Constants import ID_KEY
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOMINEES, ELECTION_JSON_KEY__NOM_NAME, \
    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, ELECTION_JSON_KEY__NOM_FACEBOOK, \
    ELECTION_JSON_KEY__NOM_EMAIL, ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOM_INSTAGRAM, \
    ELECTION_JSON_KEY__NOM_DISCORD_ID, ELECTION_JSON_KEY__NOM_SFUID
from elections.views.extractors.get_existing_nominee import get_exist_nominee
from elections.views.save_nominee.save_new_nominee_jformat import save_new_nominee_jformat
from elections.views.save_nominee.update_existing_nominees_jformat import update_existing_nominee_jformat


def save_new_or_update_existing_nominees_jformat(election, election_information):
    """
    Iterates through the list of nominees that need to be saved or updated in the given election
    they are saved by calling either update_existing_nominee_jformat or save_new_nominee_jformat

    Keyword Argument
    election -- the saved election
    election_information -- the dict that contains the nominee information that needs to be saved or updated

    Return
    error-message -- the error message if the function could not find the nominee election under the
     election_information dict or None if it could be found
    """
    logger = Loggers.get_logger()
    list_of_nominee_ids_specified_in_election = []
    list_of_speech_obj_ids_specified_in_election = []
    list_of_nominee_position_obj_ids_specified_in_election = []
    if ELECTION_JSON_KEY__NOMINEES not in election_information:
        return f"Could not find the key {ELECTION_JSON_KEY__NOMINEES} in the election_information"
    nominees = election_information[ELECTION_JSON_KEY__NOMINEES]
    for nominee in nominees:
        if ID_KEY in nominee:
            nominee_obj = get_exist_nominee(nominee[ID_KEY], election.id)
            if nominee_obj is not None:
                position_ids, speech_ids = update_existing_nominee_jformat(nominee_obj, nominee)
                list_of_nominee_ids_specified_in_election.append(nominee_obj.id)
                list_of_speech_obj_ids_specified_in_election.extend(speech_ids)
                list_of_nominee_position_obj_ids_specified_in_election.extend(position_ids)
        else:
            nominee_id, position_ids, speech_ids = save_new_nominee_jformat(
                election, nominee[ELECTION_JSON_KEY__NOM_NAME],
                nominee[ELECTION_JSON_KEY__NOM_SFUID],
                nominee[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS],
                nominee[ELECTION_JSON_KEY__NOM_FACEBOOK], nominee[ELECTION_JSON_KEY__NOM_INSTAGRAM],
                nominee[ELECTION_JSON_KEY__NOM_LINKEDIN], nominee[ELECTION_JSON_KEY__NOM_EMAIL],
                nominee[ELECTION_JSON_KEY__NOM_DISCORD_ID]
            )
            list_of_nominee_ids_specified_in_election.append(nominee_id)
            list_of_speech_obj_ids_specified_in_election.extend(speech_ids)
            list_of_nominee_position_obj_ids_specified_in_election.extend(position_ids)
    logger.info(
        "[elections/save_new_or_update_existing_nominees_jformat.py save_new_or_update_existing_nominees_jformat()]"
        f"list_of_nominee_ids_specified_in_election = {list_of_nominee_ids_specified_in_election}"
    )

    logger.info(
        "[elections/save_new_or_update_existing_nominees_jformat.py save_new_or_update_existing_nominees_jformat()]"
        f"list_of_speech_obj_ids_specified_in_election = {list_of_speech_obj_ids_specified_in_election}"
    )

    logger.info(
        "[elections/save_new_or_update_existing_nominees_jformat.py save_new_or_update_existing_nominees_jformat()]"
        f"list_of_nominee_position_obj_ids_specified_in_election = "
        f"{list_of_nominee_position_obj_ids_specified_in_election}"
    )
    # does a cleanup to ensure there are no duplicate or garbage entries remaining for either
    # the nominees, the positions they are running for, or their speeches
    current_nominee_ids_under_election = [
        nominee.id for nominee in Nominee.objects.all().filter(election_id=election.id)
    ]
    logger.info(
        "[elections/save_new_or_update_existing_nominees_jformat.py save_new_or_update_existing_nominees_jformat()]"
        f"current_nominee_ids_under_election = {current_nominee_ids_under_election}"
    )
    nominee_ids_to_delete = [
        current_nominee_id_under_election for current_nominee_id_under_election in current_nominee_ids_under_election
        if current_nominee_id_under_election not in list_of_nominee_ids_specified_in_election
    ]
    logger.info(
        "[elections/save_new_or_update_existing_nominees_jformat.py save_new_or_update_existing_nominees_jformat()]"
        f"nominee_ids_to_delete = {nominee_ids_to_delete}"
    )
    for nominee_id_to_delete in nominee_ids_to_delete:
        Nominee.objects.all().get(id=nominee_id_to_delete).delete()

    current_nominee_speech_ids_under_election = [
        speech.id for speech in NomineeSpeech.objects.all().filter(nominee__election_id=election.id)
    ]
    logger.info(
        "[elections/save_new_or_update_existing_nominees_jformat.py save_new_or_update_existing_nominees_jformat()]"
        f"current_nominee_speech_ids_under_election = {current_nominee_speech_ids_under_election}"
    )
    speeches_id_to_delete = [
        speech_id for speech_id in current_nominee_speech_ids_under_election
        if speech_id not in list_of_speech_obj_ids_specified_in_election
    ]
    logger.info(
        "[elections/save_new_or_update_existing_nominees_jformat.py save_new_or_update_existing_nominees_jformat()]"
        f"speeches_id_to_delete = {speeches_id_to_delete}"
    )
    for speech_id_to_delete in speeches_id_to_delete:
        NomineeSpeech.objects.all().get(id=speech_id_to_delete).delete()

    current_nominee_speech_ids_under_election = [
        speech.id for speech in NomineePosition.objects.all().filter(nominee_speech__nominee__election_id=election.id)
    ]
    logger.info(
        "[elections/save_new_or_update_existing_nominees_jformat.py save_new_or_update_existing_nominees_jformat()]"
        f"current_nominee_speech_ids_under_election = {current_nominee_speech_ids_under_election}"
    )
    nominee_positions_to_delete = [
        position_id
        for position_id in current_nominee_speech_ids_under_election
        if position_id not in list_of_nominee_position_obj_ids_specified_in_election
    ]
    logger.info(
        "[elections/save_new_or_update_existing_nominees_jformat.py save_new_or_update_existing_nominees_jformat()]"
        f"nominee_positions_to_delete = {nominee_positions_to_delete}"
    )
    for nominee_position_id_to_delete in nominee_positions_to_delete:
        NomineePosition.objects.all().get(id=nominee_position_id_to_delete).delete()
    return None
