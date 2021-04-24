from elections.models import Nominee, NomineeSpeech, NomineePosition
from elections.views.Constants import ELECTION_NOMINEES_KEY, NOM_ID_KEY, NOM_NAME_KEY, \
    NOM_POSITION_AND_SPEECH_KEY, NOM_FACEBOOK_KEY, NOM_LINKEDIN_KEY, NOM_EMAIL_KEY, \
    NOM_DISCORD_USERNAME_KEY
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

    list_of_nominee_ids_specified_in_election = []
    list_of_speech_obj_ids_specified_in_election = []
    list_of_nominee_position_obj_ids_specified_in_election = []
    if ELECTION_NOMINEES_KEY not in election_information:
        return f"Could not find the key {ELECTION_NOMINEES_KEY} in the election_information"
    nominees = election_information[ELECTION_NOMINEES_KEY]
    for nominee in nominees:
        if NOM_ID_KEY in nominee:
            nominee_obj = get_exist_nominee(nominee[NOM_ID_KEY], election.id)
            if nominee_obj is not None:
                position_ids, speech_ids = update_existing_nominee_jformat(nominee_obj, nominee)
                list_of_nominee_ids_specified_in_election.append(nominee_obj.id)
                list_of_speech_obj_ids_specified_in_election.extend(speech_ids)
                list_of_nominee_position_obj_ids_specified_in_election.extend(position_ids)
        else:
            nominee_id, position_ids, speech_ids = save_new_nominee_jformat(
                election, nominee[NOM_NAME_KEY], nominee[NOM_POSITION_AND_SPEECH_KEY],
                nominee[NOM_FACEBOOK_KEY], nominee[NOM_LINKEDIN_KEY], nominee[NOM_EMAIL_KEY],
                nominee[NOM_DISCORD_USERNAME_KEY]
            )
            list_of_nominee_ids_specified_in_election.append(nominee_id)
            list_of_speech_obj_ids_specified_in_election.extend(speech_ids)
            list_of_nominee_position_obj_ids_specified_in_election.extend(position_ids)

    # does a cleanup to ensure there are no duplicate or garbage entries remaining for either
    # the nominees, the positions they are running for, or their speeches
    current_nominee_ids_under_election = [
        nominee.id for nominee in Nominee.objects.all().filter(election_id=election.id)
    ]
    ids_to_delete = [
        current_nominee_id_under_election for current_nominee_id_under_election in current_nominee_ids_under_election
        if current_nominee_id_under_election not in list_of_nominee_ids_specified_in_election
    ]
    for nominee_id_to_delete in ids_to_delete:
        Nominee.objects.all().get(id=nominee_id_to_delete).delete()

    speeches_id_to_delete = [
        speech.id for speech in NomineeSpeech.objects.all().filter(nominee__election_id=election.id)
        if speech.id not in list_of_speech_obj_ids_specified_in_election
    ]
    for speech_id_to_delete in speeches_id_to_delete:
        NomineeSpeech.objects.all().get(id=speech_id_to_delete).delete()

    nominee_positions_to_delete = [
        positions.id
        for positions in NomineePosition.objects.all().filter(nominee_speech__nominee__election_id=election.id)
        if positions.id not in list_of_nominee_position_obj_ids_specified_in_election
    ]
    for nominee_position_id_to_delete in nominee_positions_to_delete:
        NomineePosition.objects.all().get(id=nominee_position_id_to_delete).delete()
    return None