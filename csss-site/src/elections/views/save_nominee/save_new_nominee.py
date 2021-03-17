import logging

from about.models import OfficerEmailListAndPositionMapping
from elections.models import Nominee, NomineeSpeech, NomineePosition
from elections.views.election_management import NOM_SPEECH_POST_KEY, NOM_POSITIONS_POST_KEY

logger = logging.getLogger('csss_site')


def save_new_nominee(election, full_name, position_names_and_speeches, facebook_link, linkedin_link,
                     email_address, discord_username):
    """
    Saves the given nominees and the relevant NomineePosition objects with the given values

    Keyword Argument
    election -- the election to save the nominee under
    full_name -- the name of the nominee
    position_names_and_speeches -- a list of the pairings of the nominee's speeches and position_names
    facebook_link -- the nominee's facebook link
    linkedin_link -- the nominee's linkedin link
    email_address -- the nominee's email address
    discord_username -- the nominee's discord username

    Return
    nominee_id -- the ID of the nominee that got saved
    position_ids -- the position IDs that was saved for the nominee
    speech_ids -- the speech IDs that were saved for the nominee
    """
    full_name = full_name.strip()
    facebook_link = facebook_link.strip()
    linkedin_link = linkedin_link.strip()
    email_address = email_address.strip()
    discord_username = discord_username.strip()
    nominee = Nominee(election=election, name=full_name, facebook=facebook_link,
                      linked_in=linkedin_link, email=email_address, discord=discord_username)
    nominee.save()
    logger.info("[elections/save_new_nominee.py save_new_nominee()]"
                f"saved nominee {nominee} under election {election}"
                )
    position_ids = []
    speech_ids = []
    for speech_and_position_pairing in position_names_and_speeches:
        speech_obj = NomineeSpeech(
            nominee=nominee, speech=speech_and_position_pairing[NOM_SPEECH_POST_KEY].strip()
        )
        speech_obj.save()
        speech_ids.append(speech_obj.id)
        for position_name in speech_and_position_pairing[NOM_POSITIONS_POST_KEY]:
            nominee_position = NomineePosition(
                position_name=position_name, nominee_speech=speech_obj,
                position_index=OfficerEmailListAndPositionMapping.objects.get(
                    position_name=position_name
                ).position_index
            )
            nominee_position.save()
            position_ids.append(nominee_position.id)
            logger.info(
                "[elections/save_new_nominee.py save_new_nominee()]"
                f"saved nominee {nominee} with position {nominee_position}"
            )
    return nominee.id, position_ids, speech_ids
