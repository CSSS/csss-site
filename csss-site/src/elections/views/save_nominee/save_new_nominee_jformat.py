import logging

from about.models import OfficerEmailListAndPositionMapping
from elections.models import Nominee, NomineeSpeech, NomineePosition
from elections.views.Constants import ELECTION_JSON_KEY__NOM_SPEECH, ELECTION_JSON_KEY__NOM_POSITION_NAMES

logger = logging.getLogger('csss_site')


def save_new_nominee_jformat(election, name, speech_and_position_pairings, facebook_link, linkedin_link,
                             email_address, discord_username):
    """
    Saves the given nominees and the relevant NomineeSpeech and NomineePosition objects with the given values

    Keyword Argument
    election -- the election to save the nominee under
    name -- the name of the nominee
    speech_and_position_pairings -- a list of the pairings of the nominee's speeches and position_names
    facebook_link -- the nominee's facebook link
    linkedin_link -- the nominee's linkedin link
    email_address -- the nominee's email address
    discord_username -- the nominee's discord username

    Return
    nominee_id -- the ID of the nominee that got saved
    position_ids -- the position IDs that was saved for the nominee
    speech_ids -- the speech IDs that were saved for the nominee
    """
    name = name.strip()
    facebook_link = facebook_link.strip()
    linkedin_link = linkedin_link.strip()
    email_address = email_address.strip()
    discord_username = discord_username.strip()
    nominee = Nominee(election=election, name=name, facebook=facebook_link,
                      linkedin=linkedin_link, email=email_address, discord=discord_username)
    nominee.save()
    logger.info("[elections/save_new_nominee_jformat.py save_new_nominee_jformat()]"
                f"saved nominee {nominee} under election {election}"
                )
    position_ids = []
    speech_ids = []
    for speech_and_position_pairing in speech_and_position_pairings:
        speech_obj = NomineeSpeech(
            nominee=nominee, speech=speech_and_position_pairing[ELECTION_JSON_KEY__NOM_SPEECH].strip()
        )
        speech_obj.save()
        speech_ids.append(speech_obj.id)
        for position_name in speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES]:
            nominee_position = NomineePosition(
                position_name=position_name, nominee_speech=speech_obj,
                position_index=OfficerEmailListAndPositionMapping.objects.get(
                    position_name=position_name, marked_for_deletion=False, elected_position=True
                ).position_index
            )
            nominee_position.save()
            position_ids.append(nominee_position.id)
            logger.info(
                "[elections/save_new_nominee_jformat.py save_new_nominee_jformat()]"
                f"saved nominee {nominee} with position {nominee_position}"
            )
    logger.info(
        "[elections/save_new_nominee_jformat.py save_new_nominee_jformat()]"
        f"returning nominee.id = {nominee.id}, position_ids = {position_ids} and speech_ids = {speech_ids}"
    )
    return nominee.id, position_ids, speech_ids
