import datetime
import logging

from about.models import OfficerEmailListAndPositionMapping
from elections.models import Election, Nominee, NomineePosition
from elections.views.election_management import ELECTION_DATE_POST_KEY, ELECTION_TYPE_POST_KEY, \
    ELECTION_WEBSURVEY_LINK_POST_KEY, ELECTION_NOMINEES_POST_KEY, NOM_NAME_POST_KEY, \
    NOM_POSITION_POST_KEY, NOM_SPEECH_POST_KEY, NOM_FACEBOOK_POST_KEY, NOM_EMAIL_POST_KEY, NOM_LINKEDIN_POST_KEY, \
    NOM_DISCORD_USERNAME_POST_KEY

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
    save_nominees(election, updated_elections_information)
    logger.info(
        "[elections/extract_from_json.py save_new_election_from_json()] election "
        f"{election} created with slug {election.slug}, "
        f"election_type={election.election_type}, date={election.date}, "
        f"websurvey={election.websurvey}, human_friendly_name={election.human_friendly_name} "
    )
    return election.slug


def update_existing_election_from_json(election, date, election_type, websurvey_link):
    election.date = datetime.datetime.strptime(f"{date}", '%Y-%m-%d %H:%M')
    election.slug, election.human_friendly_name = \
        create_slug_and_human_friendly_name_election(election.date, election_type)
    election.election_type = election_type
    election.websurvey = websurvey_link
    election.save()


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


def save_nominees(election, election_information):
    """
    Iterates through the list of nominees to save to the given election

    Keyword Argument
    election -- the saved election
    election_information -- the dict that contains the noninee information that needs to be saved
    """
    nominees = election_information[ELECTION_NOMINEES_POST_KEY]
    for nominee in nominees:
        for nominee_position in nominee[NOM_POSITION_POST_KEY]:
            nominee_position = _get_existing_nominee(
                nominee[NOM_NAME_POST_KEY], nominee_position, election
            )
            if nominee_position is None:
                save_new_nominee(election,
                                 nominee[NOM_NAME_POST_KEY], nominee[NOM_POSITION_POST_KEY],
                                 nominee[NOM_SPEECH_POST_KEY], nominee[NOM_FACEBOOK_POST_KEY],
                                 nominee[NOM_LINKEDIN_POST_KEY], nominee[NOM_EMAIL_POST_KEY],
                                 nominee[NOM_DISCORD_USERNAME_POST_KEY]
                                 )
            else:
                update_existing_nominee(
                    nominee_position, nominee[NOM_NAME_POST_KEY], nominee[NOM_POSITION_POST_KEY],
                    nominee[NOM_SPEECH_POST_KEY], nominee[NOM_FACEBOOK_POST_KEY],
                    nominee[NOM_LINKEDIN_POST_KEY], nominee[NOM_EMAIL_POST_KEY],
                    nominee[NOM_DISCORD_USERNAME_POST_KEY]
                )


def _get_existing_nominee(nominee_name, nominee_position, election):
    nominee_name = nominee_name.strip()
    nominee_position = nominee_position.strip()
    nominees = NomineePosition.objects.all().filter(
        nominee__election_id=election.id, nominee__name=nominee_name, position_name=nominee_position
    )
    if len(nominees) > 0:
        return nominees
    return None


def save_new_nominee(election, full_name, position_names, speech, facebook_link, linkedin_link,
                     email_address, discord_username):
    """
    Saves the given nominees and the relevant NomineePosition objects with the given values

    Keyword Argument
    election -- the election to save the nominee under
    full_name -- the name of the nominee
    position_names -- a list that contains all positions that the nominee is running for
    speech -- the speech for the nominee
    facebook_link -- the nominee's facebook link
    linkedin_link -- the nominee's linkedin link
    email_address -- the nominee's email address
    discord_username -- the nominee's discord username
    """
    full_name = full_name.strip()
    speech = speech.strip()
    facebook_link = facebook_link.strip()
    linkedin_link = linkedin_link.strip()
    email_address = email_address.strip()
    discord_username = discord_username.strip()
    nominee = Nominee(election=election, name=full_name, speech=speech, facebook=facebook_link,
                      linked_in=linkedin_link, email=email_address, discord=discord_username)
    nominee.save()
    logger.info("[elections/extract_from_json.py save_new_nominee()]"
                f"saved nominee {nominee} under election {election}"
                )
    for position_name in position_names:
        nominee_position = NomineePosition(
            nominee=nominee, position_name=position_name,
            position_index=OfficerEmailListAndPositionMapping.objects.get(
                position_name=position_name
            ).position_index
        )
        nominee_position.save()
        logger.info("[elections/extract_from_json.py save_new_nominee()]"
                    f"saved nominee {nominee} with position {nominee_position}"
                    )


def update_existing_nominee(nominee_position, full_name, position_name, speech, facebook_link, linkedin_link,
                            email_address, discord_username):
    full_name = full_name.strip()
    speech = speech.strip()
    facebook_link = facebook_link.strip()
    linkedin_link = linkedin_link.strip()
    email_address = email_address.strip()
    discord_username = discord_username.strip()

    nominee = nominee_position.nominee
    nominee.full_name = full_name
    nominee.speech = speech
    nominee.facebook = facebook_link
    nominee.linked_in = linkedin_link
    nominee.email = email_address
    nominee.discord = discord_username
    nominee.save()
    nominee_position.position_name = position_name
    nominee_position.position_index = OfficerEmailListAndPositionMapping.objects.get(
        position_name=position_name
    ).position_index
    nominee_position.save()
