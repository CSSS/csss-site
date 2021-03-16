from elections.models import Nominee, NomineeSpeech, NomineePosition
from elections.views.election_management import ELECTION_NOMINEES_POST_KEY, NOM_ID_POST_KEY, NOM_NAME_POST_KEY, \
    NOM_POSITION_AND_SPEECH_POST_KEY, NOM_FACEBOOK_POST_KEY, NOM_LINKEDIN_POST_KEY, NOM_EMAIL_POST_KEY, \
    NOM_DISCORD_USERNAME_POST_KEY
from elections.views.extractors.get_existing_nominee import get_exist_nominee
from elections.views.save_nominee.save_new_nominee import save_new_nominee
from elections.views.save_nominee.update_existing_nominees import update_existing_nominee


def save_new_or_update_existing_nominees(election, election_information):
    """
    Iterates through the list of nominees that need to be saved or updated in the given election

    Keyword Argument
    election -- the saved election
    election_information -- the dict that contains the nominee information that needs to be saved or updated
    """

    list_of_nominee_ids_specified_in_election = []
    list_of_speech_obj_ids_specified_in_election = []
    list_of_nominee_position_obj_ids_specified_in_election = []
    if ELECTION_NOMINEES_POST_KEY not in election_information:
        return
    nominees = election_information[ELECTION_NOMINEES_POST_KEY]
    for nominee in nominees:
        if NOM_ID_POST_KEY in nominee:
            nominee_obj = get_exist_nominee(nominee[NOM_ID_POST_KEY], election.id)
            if nominee_obj is not None:
                position_ids, speech_ids = update_existing_nominee(nominee_obj, nominee)
                list_of_nominee_ids_specified_in_election.append(nominee_obj.id)
                list_of_speech_obj_ids_specified_in_election.extend(speech_ids)
                list_of_nominee_position_obj_ids_specified_in_election.extend(position_ids)
        else:
            nominee_id, position_ids, speech_ids = save_new_nominee(
                election, nominee[NOM_NAME_POST_KEY], nominee[NOM_POSITION_AND_SPEECH_POST_KEY],
                nominee[NOM_FACEBOOK_POST_KEY], nominee[NOM_LINKEDIN_POST_KEY], nominee[NOM_EMAIL_POST_KEY],
                nominee[NOM_DISCORD_USERNAME_POST_KEY]
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
        int(speech.id)
        for speech in NomineeSpeech.objects.all().filter(nominee__election_id=election.id)
        if speech.id not in list_of_speech_obj_ids_specified_in_election
    ]
    for speech_id_to_delete in speeches_id_to_delete:
        NomineeSpeech.objects.all().get(id=speech_id_to_delete).delete()

    nominee_positions_to_delete = [
        int(positions.id)
        for positions in NomineePosition.objects.all().filter(nominee_speech__nominee__election_id=election.id)
        if positions.id not in list_of_nominee_position_obj_ids_specified_in_election
    ]
    for nominee_position_id_to_delete in nominee_positions_to_delete:
        NomineePosition.objects.all().get(id=nominee_position_id_to_delete).delete()
