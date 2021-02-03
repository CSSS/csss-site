import datetime
import json
import logging

from elections.models import Election, Nominee, NomineePosition
from elections.views.election_management import ELECTION_DATE_POST_KEY, ELECTION_TYPE_POST_KEY, \
    ELECTION_WEBSURVEY_LINK_POST_KEY, JSON_INPUT_FIELD_POST_KEY, ELECTION_NOMINEES_POST_KEY, NOM_NAME_POST_KEY, \
    NOM_POSITION_POST_KEY, NOM_SPEECH_POST_KEY, NOM_FACEBOOK_POST_KEY, NOM_EMAIL_POST_KEY, NOM_LINKEDIN_POST_KEY, \
    NOM_DISCORD_USERNAME_POST_KEY

logger = logging.getLogger('csss_site')


def validate_new_election(request):
    """Extracts the date from the election_dict and passes it off to create_new_nomination_page
    to create the election object

    Keyword Argument
    updated_elections_information -- the POST section of request

    Return
    Boolean -- true if election was saved and false if it was not
    election -- the election object, if one was created
    error_message -- populated if the election could not be saved
    """
    return _validate_and_return_information_from_new_election(json.loads(request.POST[JSON_INPUT_FIELD_POST_KEY]))


def _validate_and_return_information_from_new_election(updated_elections_information):
    """extract all the information for the election [excluding the datetime] and passes it off to
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
    dt = datetime.datetime.strptime(f"{updated_elections_information[ELECTION_DATE_POST_KEY]}", '%Y-%m-%d %H:%M')
    slug, human_friendly_name = _create_slug_and_human_friendly_name_election(dt, election_type)
    election = _create_election_object(election_type, election_websurvey, dt, slug, human_friendly_name)
    save_nominees(election, updated_elections_information)
    logger.info(
        "[elections/election_management.py process_new_election_information_from_json()] election "
        f"{election} created with slug {election.slug}, "
        f"election_type={election.election_type}, date={election.date}, "
        f"websurvey={election.websurvey}, human_friendly_name={election.human_friendly_name} "
    )
    return election.slug


def _create_slug_and_human_friendly_name_election(dt, chosen_election_type):
    """create the slug and human friendly name for election using its date and election type

    Keyword Argument
    dt -- the datetime for the election
    chosen_election_type -- indicates whether the election is a general election of by election

    Return
    slug -- the slug for the election
    human_friendly_name -- the human friendly name for the election
    """
    slug = f"{dt.strftime('%Y-%m-%d')}-{chosen_election_type}"
    human_friendly_election_type = [valid_election_type_choice[1]
                                    for valid_election_type_choice in Election.election_type_choices
                                    if valid_election_type_choice[0] == chosen_election_type
                                    ][0]
    human_friendly_name = f"{human_friendly_election_type}: {dt.strftime('%Y-%m-%d')}"
    return slug, human_friendly_name


def _create_election_object(election_type, election_websurvey, dt, slug, human_friendly_name):
    """
    Create a new election given the election information

    Keyword Arguments
    election_type -- indicates whether the election is a general election of by election
    election_websurvey -- the link to the election's websurvey
    dt - the date and time of the election
    slug - the url for the election
    human_friendly_name -- the human friendly name of the election

    Return
    the election object

    """
    election = Election(slug=slug, election_type=election_type, date=dt,
                        websurvey=election_websurvey, human_friendly_name=human_friendly_name)
    election.save()
    return election


def save_nominees(election, election_information):
    nominees = election_information[ELECTION_NOMINEES_POST_KEY]
    for nominee in nominees:
        save_new_nominee(election,
                         nominee[NOM_NAME_POST_KEY], nominee[NOM_POSITION_POST_KEY],
                         nominee[NOM_SPEECH_POST_KEY], nominee[NOM_FACEBOOK_POST_KEY],
                         nominee[NOM_LINKEDIN_POST_KEY], nominee[NOM_EMAIL_POST_KEY],
                         nominee[NOM_DISCORD_USERNAME_POST_KEY]
                         )


def save_new_nominee(election, full_name, position_names, speech, facebook_link, linkedin_link,
                     email_address, discord_username):
    nominee = Nominee(election=election, name=full_name, speech=speech, facebook=facebook_link,
                      linked_in=linkedin_link, email=email_address, discord=discord_username)
    nominee.save()
    for position_name in position_names:
        NomineePosition(nominee=nominee, officer_position=position_name).save()
