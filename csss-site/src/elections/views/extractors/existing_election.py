import datetime

from about.models import OfficerEmailListAndPositionMapping
from elections.models import Nominee, NomineeSpeech, NomineePosition
from elections.views.election_management import ELECTION_NOMINEES_POST_KEY, NOM_POSITION_AND_SPEECH_POST_KEY, \
    NOM_ID_POST_KEY, NOM_POSITIONS_POST_KEY, NOM_NAME_POST_KEY, NOM_SPEECH_POST_KEY, NOM_FACEBOOK_POST_KEY, \
    NOM_LINKEDIN_POST_KEY, NOM_EMAIL_POST_KEY, NOM_DISCORD_USERNAME_POST_KEY, NOM_POSITION_POST_KEY
from elections.views.extractors.extract_from_json import create_slug_and_human_friendly_name_election, save_new_nominee


def update_existing_election_from_json(election, date, election_type, websurvey_link):
    election.date = datetime.datetime.strptime(f"{date}", '%Y-%m-%d %H:%M')
    election.slug, election.human_friendly_name = \
        create_slug_and_human_friendly_name_election(election.date, election_type)
    election.election_type = election_type
    election.websurvey = websurvey_link
    election.save()


def save_new_or_update_existing_nominees(election, election_information):
    """
    Iterates through the list of nominees to saved or updated in the given election

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
            nominee_obj = _get_exist_nominee(nominee[NOM_ID_POST_KEY], election.id)
            if nominee_obj is not None:
                position_ids, speech_ids = _update_existing_nominee(nominee_obj, nominee)
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
            # nominee_position_obj = None
            # speech_and_position_pairings = nominee[NOM_POSITION_AND_SPEECH_POST_KEY]
            # for speech_and_position_pairing in speech_and_position_pairings:
            #     for nominee_position in speech_and_position_pairing[NOM_POSITIONS_POST_KEY]:
            #         # tries to first see if the specified position exists for the given nominee on the given election
            #         # in the db
            #         if NOM_ID_POST_KEY in nominee:
            #             nominee_position_obj = _get_existing_nominee(
            #                 nominee[NOM_ID_POST_KEY], nominee_position, election.id
            #             )
            #         if nominee_position_obj is not None:
            #             # if the specified position exists for the given nominee on the given election
            #             nominee_position_obj_id, speech_obj_id = update_existing_nominee(
            #                 nominee_position_obj, nominee[NOM_NAME_POST_KEY], nominee_position,
            #                 speech_and_position_pairing[NOM_SPEECH_POST_KEY], nominee[NOM_FACEBOOK_POST_KEY],
            #                 nominee[NOM_LINKEDIN_POST_KEY], nominee[NOM_EMAIL_POST_KEY],
            #                 nominee[NOM_DISCORD_USERNAME_POST_KEY]
            #             )
            #             # these are recorded so that after all the nominees are updated, any duplicated or superfluous
            #             # db entries can be removed by ensuring its not a record with an ID recorded below
            #             list_of_nominee_ids_specified_in_election.append(int(NOM_ID_POST_KEY))
            #             list_of_speech_obj_ids_specified_in_election.append(speech_obj_id)
            #             list_of_nominee_position_obj_ids_specified_in_election.append(nominee_position_obj_id)
            # if nominee_position_obj is None:
            #     # it comes here if the nominee had never been saved for the given election

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


def _get_exist_nominee(nominee_id, election_id):
    nominees = Nominee.objects.all().filter(
        election_id=election_id,
        id=nominee_id
    )
    if len(nominees) > 0:
        return nominees[0]
    return None


def _update_existing_nominee(nominee_obj, nominee):
    """
    Updates the specified nominee position

    Keyword Argument

    """
    list_of_speech_obj_ids_specified_in_election = []
    list_of_nominee_position_obj_ids_specified_in_election = []

    name = nominee[NOM_NAME_POST_KEY].strip()
    facebook_link = nominee[NOM_FACEBOOK_POST_KEY].strip()
    linkedin_link = nominee[NOM_LINKEDIN_POST_KEY].strip()
    email_address = nominee[NOM_EMAIL_POST_KEY].strip()
    discord_username = nominee[NOM_DISCORD_USERNAME_POST_KEY].strip()
    speech_and_position_pairings = nominee[NOM_POSITION_AND_SPEECH_POST_KEY]
    for speech_and_positions in speech_and_position_pairings:
        user_specified_speech_id = None if NOM_ID_POST_KEY not in speech_and_positions else speech_and_positions[
            NOM_ID_POST_KEY]
        if user_specified_speech_id is None:
            speech_obj = NomineeSpeech()
        else:
            speech_obj = NomineeSpeech.objects.get(
                nominee__election_id=nominee_obj.election.id,
                id=user_specified_speech_id
            )
        speech_obj.speech = speech_and_positions[NOM_SPEECH_POST_KEY]
        speech_obj.nominee = nominee_obj
        speech_obj.save()
        list_of_speech_obj_ids_specified_in_election.append(speech_obj.id)
        for position_name_dict in speech_and_positions[NOM_POSITIONS_POST_KEY]:
            if type(position_name_dict) is dict:
                user_specified_position_id = None \
                    if not (NOM_ID_POST_KEY in position_name_dict
                            and f"{position_name_dict[NOM_ID_POST_KEY]}".isdigit()) \
                    else position_name_dict[NOM_ID_POST_KEY]
                user_specified_position_name = position_name_dict[NOM_POSITION_POST_KEY]
            else:
                user_specified_position_id = None
                user_specified_position_name = position_name_dict
            if user_specified_position_id is not None:
                position = NomineePosition.objects.get(id=user_specified_position_id)
            else:
                position = NomineePosition()
            position.position_name = user_specified_position_name
            position.position_index = OfficerEmailListAndPositionMapping.objects.get(
                position_name=user_specified_position_name
            ).position_index
            position.nominee_speech = speech_obj
            position.save()
            list_of_nominee_position_obj_ids_specified_in_election.append(position.id)
    nominee_obj.full_name = name
    nominee_obj.facebook = facebook_link
    nominee_obj.linked_in = linkedin_link
    nominee_obj.email = email_address
    nominee_obj.discord = discord_username
    nominee_obj.save()
    return list_of_nominee_position_obj_ids_specified_in_election, list_of_speech_obj_ids_specified_in_election


def _get_existing_nominee(nominee_id, nominee_position, election_id):
    """
    Tries to determine if the specified nominee position already exists under the given election

    Keyword Argument
    nominee_id -- the id for the nominee that needs to be updated
    nominee_position -- the name of the position that the nominee is running for
    election_id -- the ID for the election that the nominee is  running under

    Return
    None if no such NomineePosition exists, otherwise its the NomineePosition that corresponds to the specified
    nominee, position and election
    """
    nominee_position = nominee_position.strip()
    nominees = NomineePosition.objects.all().filter(
        nominee_speech__nominee__election_id=election_id,
        position_name=nominee_position,
        nominee_speech__nominee_id=int(nominee_id)
    )
    if len(nominees) > 0:
        return nominees[0]
    return None


def update_existing_nominee(nominee_position_obj, full_name, position_name, speech, facebook_link, linkedin_link,
                            email_address, discord_username):
    """
    Updates the specified nominee position

    Keyword Argument

    """
    full_name = full_name.strip()
    speech = speech.strip()
    facebook_link = facebook_link.strip()
    linkedin_link = linkedin_link.strip()
    email_address = email_address.strip()
    discord_username = discord_username.strip()

    speech_obj = nominee_position_obj.nominee_speech
    nominee_obj = speech_obj.nominee

    nominee_position_obj.position_name = position_name
    nominee_position_obj.position_index = OfficerEmailListAndPositionMapping.objects.get(
        position_name=position_name
    ).position_index
    speech_obj.speech = speech
    nominee_obj.full_name = full_name
    nominee_obj.facebook = facebook_link
    nominee_obj.linked_in = linkedin_link
    nominee_obj.email = email_address
    nominee_obj.discord = discord_username

    nominee_position_obj.save()
    speech_obj.save()
    nominee_obj.save()
    return nominee_position_obj.id, speech_obj.id
