from about.models import OfficerEmailListAndPositionMapping
from elections.models import NomineeSpeech, NomineePosition
from elections.views.Constants import NOM_NAME_KEY, NOM_FACEBOOK_KEY, NOM_LINKEDIN_KEY, \
    NOM_EMAIL_KEY, NOM_DISCORD_USERNAME_KEY, NOM_POSITION_AND_SPEECH_KEY, NOM_ID_KEY, \
    NOM_SPEECH_KEY, NOM_POSITIONS_KEY, NOM_POSITION_KEY


def update_existing_nominee_jformat(nominee_obj, nominee):
    """
    Updates the specified nominee position

    Keyword Argument
    nominee_obj -- the nominee that needs its info and speech and position updated
    nominee -- the JSON that contains the updated info about the nominee

    Return
    position_ids -- the position IDs that was saved for the nominee
    speech_ids -- the speech IDs that were saved for the nominee
    """
    list_of_speech_obj_ids_specified_in_election = []
    list_of_nominee_position_obj_ids_specified_in_election = []

    speech_and_position_pairings = nominee[NOM_POSITION_AND_SPEECH_KEY]
    for speech_and_position_pairing in speech_and_position_pairings:
        user_specified_speech_id = get_user_specified_speech_id(speech_and_position_pairing)
        if user_specified_speech_id is None:
            speech_obj = NomineeSpeech()
        else:
            speech_obj = NomineeSpeech.objects.get(
                nominee__election_id=nominee_obj.election.id,
                id=int(user_specified_speech_id)
            )
        speech_obj.speech = speech_and_position_pairing[NOM_SPEECH_KEY]
        speech_obj.nominee = nominee_obj
        speech_obj.save()
        list_of_speech_obj_ids_specified_in_election.append(speech_obj.id)
        for position_name_dict in speech_and_position_pairing[NOM_POSITIONS_KEY]:
            if type(position_name_dict) is dict:
                user_specified_position_name = position_name_dict[NOM_POSITION_KEY]
                position = NomineePosition.objects.get(id=get_user_specified_position_id(position_name_dict))
            else:
                user_specified_position_name = position_name_dict
                position = NomineePosition()
            position.position_name = user_specified_position_name
            position.position_index = OfficerEmailListAndPositionMapping.objects.get(
                position_name=user_specified_position_name
            ).position_index
            position.nominee_speech = speech_obj
            position.save()
            list_of_nominee_position_obj_ids_specified_in_election.append(position.id)
    nominee_obj.name = nominee[NOM_NAME_KEY].strip()
    nominee_obj.facebook = nominee[NOM_FACEBOOK_KEY].strip()
    nominee_obj.linked_in = nominee[NOM_LINKEDIN_KEY].strip()
    nominee_obj.email = nominee[NOM_EMAIL_KEY].strip()
    nominee_obj.discord = nominee[NOM_DISCORD_USERNAME_KEY].strip()
    nominee_obj.save()
    return list_of_nominee_position_obj_ids_specified_in_election, list_of_speech_obj_ids_specified_in_election


def get_user_specified_speech_id(speech_and_position_pairing):
    """
    Returns the ID if found in the dict speech_and_position_pairing or returns None otherwise
    """
    return None if NOM_ID_KEY not in speech_and_position_pairing else speech_and_position_pairing[NOM_ID_KEY]


def get_user_specified_position_id(position_name_dict):
    """
    Returns the ID if found in the dict position_name_dict or returns None otherwise
    """
    return position_name_dict[NOM_ID_KEY] if NOM_ID_KEY in position_name_dict else None
