import datetime
import logging

from about.models import OfficerEmailListAndPositionMapping
from elections.models import Election, Nominee, NomineePosition, NomineeSpeech
from elections.views.election_management import ELECTION_DATE_POST_KEY, ELECTION_TYPE_POST_KEY, \
    ELECTION_WEBSURVEY_LINK_POST_KEY, NOM_POSITIONS_POST_KEY, NOM_SPEECH_POST_KEY

logger = logging.getLogger('csss_site')


def save_new_election_from_json(updated_elections_information):
    """
    extract all the information for the election [excluding the datetime] and passes it off to
    save_new_election_to_db to create the election object before returning it back

    Keyword Argument
    dt -- the datetime representation for the election's date
    updated_elections_information -- the POST section of request

    Return
    Boolean -- true if election was saved and false if it was not
    election -- the election object, if one was created
    error_message -- populated if the election could not be saved
    """
    election_type = updated_elections_information[ELECTION_TYPE_POST_KEY]
    election_websurvey = updated_elections_information[ELECTION_WEBSURVEY_LINK_POST_KEY]
    election_date = datetime.datetime.strptime(
        f"{updated_elections_information[ELECTION_DATE_POST_KEY]}", '%Y-%m-%d %H:%M'
    )
    slug, human_friendly_name = create_slug_and_human_friendly_name_election(election_date, election_type)
    election = create_election_object(election_type, election_websurvey, election_date, slug, human_friendly_name)
    # save_new_or_update_existing_nominees(election, updated_elections_information)
    logger.info(
        "[elections/extract_from_json.py save_new_election_from_json()] election "
        f"{election} created with slug {election.slug}, "
        f"election_type={election.election_type}, date={election.date}, "
        f"websurvey={election.websurvey}, human_friendly_name={election.human_friendly_name} "
    )
    return election.slug


def create_slug_and_human_friendly_name_election(election_date, chosen_election_type):
    """create the slug and human friendly name for election using its date and election type

    Keyword Argument
    election_date -- the datetime for the election
    chosen_election_type -- indicates whether the election is a general election of by election

    Return
    slug -- the slug for the election
    human_friendly_name -- the human friendly name for the election
    """
    human_friendly_election_type = [
        valid_election_type_choice[1]
        for valid_election_type_choice in Election.election_type_choices
        if valid_election_type_choice[0] == chosen_election_type
    ][0]
    return f"{election_date.strftime('%Y-%m-%d')}-{chosen_election_type}", \
           f"{human_friendly_election_type}: {election_date.strftime('%Y-%m-%d')}"


def create_election_object(election_type, election_websurvey, election_date, slug, human_friendly_name):
    """
    Create a new election given the election information

    Keyword Arguments
    election_type -- indicates whether the election is a general election of by election
    election_websurvey -- the link to the election's websurvey
    election_date - the date and time of the election
    slug - the url for the election
    human_friendly_name -- the human friendly name of the election

    Return
    the election object

    """
    election = Election(slug=slug, election_type=election_type, date=election_date,
                        websurvey=election_websurvey, human_friendly_name=human_friendly_name)
    election.save()
    return election


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
    """
    full_name = full_name.strip()
    facebook_link = facebook_link.strip()
    linkedin_link = linkedin_link.strip()
    email_address = email_address.strip()
    discord_username = discord_username.strip()
    nominee = Nominee(election=election, name=full_name, facebook=facebook_link,
                      linked_in=linkedin_link, email=email_address, discord=discord_username)
    nominee.save()
    logger.info("[elections/extract_from_json.py save_new_nominee()]"
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
                "[elections/extract_from_json.py save_new_nominee()]"
                f"saved nominee {nominee} with position {nominee_position}"
            )
    return nominee.id, position_ids, speech_ids
