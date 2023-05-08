from about.models import OfficerEmailListAndPositionMapping
from about.views.input_new_officers.enter_new_officer_info.utils.get_discord_username_and_nickname import \
    get_discord_username_and_nickname
from csss.setup_logger import Loggers
from elections.models import Nominee, NomineeSpeech, NomineePosition
from elections.views.Constants import NA_STRING
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOM_SPEECH, \
    ELECTION_JSON_KEY__NOM_POSITION_NAMES


def save_new_nominee_jformat(election, full_name, sfuid, speech_and_position_pairings, facebook_link, instagram_link,
                             linkedin_link, email_address, discord_id, nominee_link=None,
                             election_officer_request=True):
    """
    Saves the given nominees and the relevant NomineeSpeech and NomineePosition objects with the given values

    Keyword Argument
    election -- the election to save the nominee under
    full_name -- the name of the nominee
    sfuid -- the SFU ID of the nominee
    speech_and_position_pairings -- a list of the pairings of the nominee's speeches and position_names
    facebook_link -- the nominee's facebook link
    instagram_link -- the nominee's Instagram link
    linkedin_link -- the nominee's linkedin link
    email_address -- the nominee's email address
    discord_id -- the nominee's discord ID
    nominee_link -- the nominee_link to associate with the nominee being saved
    election_officer_request -- indicates if the page is being accessed by the election officer

    Return
    nominee_id -- the ID of the nominee that got saved
    position_ids -- the position IDs that was saved for the nominee
    speech_ids -- the speech IDs that were saved for the nominee
    """
    logger = Loggers.get_logger()
    full_name = full_name.strip()
    facebook_link = facebook_link.strip() if facebook_link is not None else None
    instagram_link = instagram_link.strip() if instagram_link is not None else None
    linkedin_link = linkedin_link.strip() if facebook_link is not None else None
    email_address = email_address.strip() if facebook_link is not None else None
    discord_username = NA_STRING
    discord_nickname = NA_STRING
    discord_id = discord_id.strip() if facebook_link is not None else None
    if election_officer_request:
        sfuid = sfuid.strip()
    if not election_officer_request:
        if nominee_link is None:
            sfuid = None
        else:
            sfuid = nominee_link.nominee.get_sfuid \
                if nominee_link.nominee is not None else nominee_link.get_sfuid
    if discord_id != NA_STRING:
        success, error_message, discord_username, discord_nickname = get_discord_username_and_nickname(discord_id)

    nominee = Nominee(election=election, full_name=full_name, sfuid=sfuid, facebook=facebook_link,
                      instagram=instagram_link, linkedin=linkedin_link, email=email_address,
                      discord_username=discord_username, discord_nickname=discord_nickname, discord_id=discord_id
                      )
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
                    position_name=position_name, marked_for_deletion=False, elected_via_election_officer=True
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
    if nominee_link is not None:
        nominee_link.nominee = nominee
        nominee_link.save()
    return nominee.id, position_ids, speech_ids
