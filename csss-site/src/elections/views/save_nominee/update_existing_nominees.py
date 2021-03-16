from about.models import OfficerEmailListAndPositionMapping
from elections.models import NomineeSpeech, NomineePosition
from elections.views.election_management import NOM_NAME_POST_KEY, NOM_FACEBOOK_POST_KEY, NOM_LINKEDIN_POST_KEY, \
    NOM_EMAIL_POST_KEY, NOM_DISCORD_USERNAME_POST_KEY, NOM_POSITION_AND_SPEECH_POST_KEY, NOM_ID_POST_KEY, \
    NOM_SPEECH_POST_KEY, NOM_POSITIONS_POST_KEY, NOM_POSITION_POST_KEY


def update_existing_nominee(nominee_obj, nominee):
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

    name = nominee[NOM_NAME_POST_KEY].strip()
    facebook_link = nominee[NOM_FACEBOOK_POST_KEY].strip()
    linkedin_link = nominee[NOM_LINKEDIN_POST_KEY].strip()
    email_address = nominee[NOM_EMAIL_POST_KEY].strip()
    discord_username = nominee[NOM_DISCORD_USERNAME_POST_KEY].strip()
    speech_and_position_pairings = nominee[NOM_POSITION_AND_SPEECH_POST_KEY]
    for speech_and_positions in speech_and_position_pairings:
        user_specified_speech_id = None if NOM_ID_POST_KEY not in speech_and_positions \
            else speech_and_positions[NOM_ID_POST_KEY]
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
