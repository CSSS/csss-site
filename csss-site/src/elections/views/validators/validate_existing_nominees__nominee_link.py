from elections.models import Nominee
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOM_NAME, ELECTION_JSON_KEY__NOM_FACEBOOK, \
    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, ELECTION_JSON_KEY__NOM_LINKEDIN, \
    ELECTION_JSON_KEY__NOM_EMAIL, ELECTION_JSON_KEY__NOM_DISCORD
from elections.views.validators.validate_existing_nominee_jformat import validate_existing_nominee_jformat


def validate_existing_nominee__nominee_link(election_id, nominee_link_id, nominee_info):
    """
    Ensures that the nominee info is valid and ensure that the name entered hasn't been used by another nominee

    Keyword Argument:
    election_id -- the ID of the election the nominee belongs to
    nominee_link_id - the ID of the Nominee_Link object attached to the nominee being updated
    nominee_info -- the new info for the nominee that has to be validated

    Return
    Boolean -- indicates whether or not nominee information is valid which happens when any of the
    specified fields are empty
    error_message -- the error message if the nominees had an invalid input
    """
    nominee_names_so_far = [nominee.name for nominee in Nominee.objects.all().filter(
        election_id=election_id).exclude(nomineelink__id=nominee_link_id)
                            ]
    speech_ids_so_far = []
    position_ids_so_far = []
    return validate_existing_nominee_jformat(
        nominee_names_so_far, speech_ids_so_far, position_ids_so_far,
        nominee_info[ELECTION_JSON_KEY__NOM_NAME], nominee_info[ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS],
        nominee_info[ELECTION_JSON_KEY__NOM_FACEBOOK], nominee_info[ELECTION_JSON_KEY__NOM_LINKEDIN],
        nominee_info[ELECTION_JSON_KEY__NOM_EMAIL], nominee_info[ELECTION_JSON_KEY__NOM_DISCORD], election_id)
