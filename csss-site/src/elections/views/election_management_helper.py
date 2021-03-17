import datetime
import logging

from about.models import OfficerEmailListAndPositionMapping
from elections.models import Election, Nominee
from elections.views.election_management import NOM_NAME_POST_KEY, NOM_POSITIONS_POST_KEY, NOM_SPEECH_POST_KEY, \
    NOM_FACEBOOK_POST_KEY, NOM_LINKEDIN_POST_KEY, NOM_EMAIL_POST_KEY, NOM_DISCORD_USERNAME_POST_KEY, \
    ELECTION_DATE_POST_KEY, ELECTION_TIME_POST_KEY, ELECTION_TYPE_POST_KEY, \
    ELECTION_WEBSURVEY_LINK_POST_KEY
from elections.views.extractors.get_election_from_json import save_new_election_from_json
from elections.views.extractors.get_election_slug_and_name import gete_slug_and_human_friendly_name_election

logger = logging.getLogger('csss_site')


def _create_new_election_from_webform(updated_elections_information):
    """Extracts the date from the election_dict and passes it off to create_new_nomination_page to create
    the election object before it is passed back to this function and saved

    Keyword Argument
    updated_elections_information -- the POST section of request

    Return
    election -- the saved election object
    """
    dt = datetime.datetime.strptime(
        f"{updated_elections_information[ELECTION_DATE_POST_KEY]} "
        f"{updated_elections_information[ELECTION_TIME_POST_KEY]}",
        '%Y-%m-%d %H:%M'
    )
    success, election_page, error_message = save_new_election_from_json(
        dt, updated_elections_information
    )
    election_page.save()
    logger.info(
        "[elections/election_management.py _create_new_election_from_webform()] election "
        f"{election_page} created with slug {election_page.slug}, election_type={election_page.election_type}, "
        f"date={election_page.date}, websurvey={election_page.websurvey}, "
        f"human_friendly_name={election_page.human_friendly_name} "
    )
    return election_page


def _save_nominees_for_new_election_from_webform(election, updated_elections_information):
    """takes in a list of nominees' information and save them as nominee objects

    Keyword Arguments
    election -- the election object that the new nominees belong to
    updated_elections_information -- the POST section of request
    """
    for nominee_index in range(len(updated_elections_information[NOM_NAME_POST_KEY])):
        success, nominee, error_message = _validate_and_return_new_nominee(
            updated_elections_information[NOM_NAME_POST_KEY][nominee_index],
            updated_elections_information[NOM_POSITIONS_POST_KEY][nominee_index],
            updated_elections_information[NOM_SPEECH_POST_KEY][nominee_index],
            updated_elections_information[NOM_FACEBOOK_POST_KEY][nominee_index],
            updated_elections_information[NOM_LINKEDIN_POST_KEY][nominee_index],
            updated_elections_information[NOM_EMAIL_POST_KEY][nominee_index],
            updated_elections_information[NOM_DISCORD_USERNAME_POST_KEY][nominee_index]
        )
        if nominee is not None:
            nominee.election = election
            nominee.save()


def _validate_and_return_new_nominee(full_name, position_names, speech, facebook_link, linkedin_link,
                                     email_address, discord_username):
    """Takes in the info of a single nominee [except its election] and creates the nominee object
    that will need to be saved

    Keyword Arguments
    full_name -- the full name of the nominee
    position_names -- the officer positions the nominee is running for
    speech -- the nominee's speech for the position
    facebook_link -- the link to the nominee's facebook profile
    linkedin_link -- the link to the nominee's linkedin page
    email_address -- the nominee's email address
    discord_username -- the nominee's discord username
    nominee_index -- the index of the nominee which determines in what order the nominee will be shown on
    the nomination page

    Return
    Boolean -- indicates whether or not nominee information is valid which happens when any of the
    specified fields are empty
    nominee -- the  nominee object created with the input, or None if full_name is set to "NONE"
    error_message -- the error message if the nominee could not be created
    """

    if len(full_name.strip()) == 0:
        return False, None, "No valid name detected for one of the nominees"
    if len(position_names) == 0 or not isinstance(position_names, list):
        return False, None, f"No valid position detected for nominee {full_name}"
    for position_name in position_names:
        if len(OfficerEmailListAndPositionMapping.objects.all().filter(position_name=position_name)) == 0:
            return False, None, f"Position {position_name} detected for nominee {full_name} is not valid"
    if len(speech) == 0:
        return False, None, f"No valid speech detected for nominee" \
                            f" {full_name}, please set to \"NONE\" if there is no speech"
    if len(facebook_link) == 0:
        return False, None, f"No valid facebook link detected for nominee" \
                            f" {full_name}, please set to \"NONE\" if there is no facebook link"
    if len(linkedin_link) == 0:
        return False, None, f"No valid linkedin link detected for nominee" \
                            f" {full_name}, please set to \"NONE\" if there is no linkedin link"
    if len(email_address) == 0:
        return False, None, f"No valid email detected for nominee" \
                            f" {full_name}, please set to \"NONE\" if there is no email"
    if len(discord_username) == 0:
        return False, None, f"No valid discord username detected for nominee" \
                            f" {full_name}, please set to \"NONE\" if there is no discord " \
                            f"username "
    if full_name != 'NONE':  # if full_name is NONE, then it is a nominee that needs to be removed
        return True, Nominee(name=full_name, position_name=position_name,
                             speech=speech,
                             facebook=facebook_link, linked_in=linkedin_link, email=email_address,
                             discord=discord_username,
                             position_index=0
                             ), None
    return True, None, None


def _get_existing_election_by_id(election_id):
    """Returns an election page by id

    Keyword Argument
    election_id -- the id for the election to return

    Return
    elections -- the election object for the election the user wants
    """
    try:
        elections = Election.objects.get(id=election_id)
    except Exception:
        logger.info("[elections/election_management.py _get_existing_election_by_id()] unable to find an election by "
                    f"id '{election_id}'")
        return None
    return elections


def _validate_information_for_existing_election_from_webform_and_return_it(election,
                                                                           updated_elections_information):
    """Extracts the date from the election_dict and passes it off to the next function to update the election page
    before returning the created nomination page that still needs to be saved

    Keyword Argument
    election -- the election object that needs to be updated
    updated_elections_information -- the POST section of request that contains the new information

    Return
    election -- the election object, if it existed. otherwise None
    """
    dt = datetime.datetime.strptime(
        f"{updated_elections_information[ELECTION_DATE_POST_KEY]} "
        f"{updated_elections_information[ELECTION_TIME_POST_KEY]}",
        '%Y-%m-%d %H:%M')
    success, election, error_message = \
        _validate_information_for_existing_election_obj_and_return_it(dt,
                                                                      election,
                                                                      updated_elections_information)
    return election


def _validate_information_for_existing_election_obj_and_return_it(dt, election, updated_elections_information):
    """extracts all the information for the election [excluding the datetime] and creates the election object
    that still needs to be saved

    Keyword Argument
    dt -- the datetime representation for the elections's date
    election -- the election objet that needs to be updated
    updated_elections_information -- the POST section of request

    Return
    Boolean -- true if election had been saved and false if it was not
    election -- the election object, if one was created
    error_message -- populated if the election could not be saved
    """
    valid_election_type_choices = [election_type_choice[0] for election_type_choice in
                                   Election.election_type_choices]
    chosen_election_type = updated_elections_information[ELECTION_TYPE_POST_KEY]
    if chosen_election_type not in valid_election_type_choices:
        logger.error(
            f"[elections/election_management.py _validate_information_for_existing_election_obj_and_return_it()] "
            f"given election_type of {chosen_election_type} is not one of the valid options:"
            f" {valid_election_type_choices}"
        )
        return False, None, f"the election type you entered {chosen_election_type} " \
                            f"is not one of the valid options: {valid_election_type_choices}"
    election_websurvey = updated_elections_information[ELECTION_WEBSURVEY_LINK_POST_KEY]
    slug, human_friendly_name = gete_slug_and_human_friendly_name_election(dt, chosen_election_type)
    election.slug = slug
    election.human_friendly_name = human_friendly_name
    election.election_type = chosen_election_type
    election.date = dt
    election.websurvey = election_websurvey
    return True, election, None


def _validate_nominees_information_for_existing_election_from_webform_and_return_them(election,
                                                                                      updated_elections_information):
    """Updates the nominees for an election that are inputted using the WebForm

    Keyword Arguments
    election -- the election object that needs to be updated
    updated_elections_information -- the POST section of request
    """
    position_index = 0
    existing_nominees = Nominee.objects.all().filter(nomination_page_id=election.id)
    existing_nominees_names = [existing_nominee.name for existing_nominee in existing_nominees]
    new_nominees_names = []
    for nominee_index in range(len(updated_elections_information[NOM_NAME_POST_KEY])):
        full_name = updated_elections_information[NOM_NAME_POST_KEY][nominee_index]
        position_name = updated_elections_information[NOM_POSITIONS_POST_KEY][nominee_index]
        speech = updated_elections_information[NOM_SPEECH_POST_KEY][nominee_index]
        facebook_link = updated_elections_information[NOM_FACEBOOK_POST_KEY][nominee_index]
        linkedin_link = updated_elections_information[NOM_LINKEDIN_POST_KEY][nominee_index]
        email_address = updated_elections_information[NOM_EMAIL_POST_KEY][nominee_index]
        discord_username = updated_elections_information[NOM_DISCORD_USERNAME_POST_KEY][nominee_index]
        if full_name not in existing_nominees_names:
            success, nominee, error_message = \
                _validate_and_return_new_nominee(
                    full_name, position_name, speech, facebook_link, linkedin_link,
                    email_address, discord_username, position_index
                )
            if success and nominee is not None:
                nominee.election = election
                nominee.save()
                logger.info(
                    "[elections/election_management.py _validate_nominees_information_for_existing_election_from"
                    f"_webform_and_return_them()] saved user full_name={full_name} "
                    f"position_name={position_name}"
                    f" facebook_link={facebook_link} linkedin_link={linkedin_link} "
                    f"email_address={email_address} discord_username={discord_username}"
                )
                new_nominees_names.append(full_name)
                position_index += 1
        else:
            success, nominee, error_message = \
                _validate_new_information_for_existing_nominee_for_existing_election_and_return_it(
                    election, full_name, position_name, speech, facebook_link, linkedin_link, email_address,
                    discord_username, position_index
                )
            if success and nominee is not None:
                nominee.save()
                logger.info(
                    "[elections/election_management.py _validate_nominees_information_for_existing_"
                    "election_from_webform_and_return_them()] updated user "
                    f"full_name={full_name} position_name={position_name}"
                    f" facebook_link={facebook_link} linkedin_link={linkedin_link} "
                    f"email_address={email_address} discord_username={discord_username}"
                )
                new_nominees_names.append(full_name)
                position_index += 1
    for existing_nominee in existing_nominees:
        if existing_nominee.name not in new_nominees_names:
            existing_nominee.delete()


def _validate_new_information_for_existing_nominee_for_existing_election_and_return_it(
        election, full_name, position_name, speech, facebook_link, linkedin_link, email_address,
        discord_username, nominee_index):
    """Takes in the info of a single nominee to save it under given nomination page

    Keyword Arguments
    election -- the nomination page to save the nominee under
    full_name -- the full name of the nominee
    position_name -- the officer position the nominee is running for
    speech -- the nominee's speech for the position
    facebook_link -- the link to the nominee's facebook profile
    linkedin_link -- the link to the nominee's linkedin page
    email_address -- the nominee's email address
    discord_username -- the nominee's discord username
    nominee_index -- the index of the nominee which determines in what order the nominee
    will be shown on the nomination page

    Return
    Boolean -- false if the nominee could not be found.
    nominee -- the nominee object that needs to be saved. set to NULL if full_name is set to None
    error_message -- the error message if there was an error
    """
    if full_name != 'NONE':
        if len(full_name.strip()) == 0:
            return False, None, "No valid name detected for one of the nominees"
        if len(position_name.strip()) == 0:
            return False, None, f"No valid position detected for nominee {full_name}"
        if len(speech) == 0:
            return False, None, f"No valid speech detected for nominee" \
                                f" {full_name}, please set to \"NONE\" if there is no speech"
        if len(facebook_link) == 0:
            return False, None, f"No valid facebook link detected for nominee" \
                                f" {full_name}, please set to \"NONE\" if there is no facebook link"
        if len(linkedin_link) == 0:
            return False, None, f"No valid linkedin link detected for nominee" \
                                f" {full_name}, please set to \"NONE\" if there is no linkedin link"
        if len(email_address) == 0:
            return False, None, f"No valid email detected for nominee" \
                                f" {full_name}, please set to \"NONE\" if there is no email"
        if len(discord_username) == 0:
            return False, None, f"No valid discord username detected for nominee" \
                                f" {full_name}, please set to \"NONE\" if there is no discord " \
                                f"username "
        try:
            nominee = Nominee.objects.get(election=election, name=full_name,
                                          position_name=position_name)
        except Nominee.DoesNotExist:
            logger.info(
                "[elections/election_management.py _validate_new_information_for_existing_nominee_for_e"
                "xisting_election_and_return_it()] unable to find "
                f"nominee full_name={full_name} position_name={position_name} for election {election}"
            )
            return False, None, f"The nominee {full_name} for position {position_name} could not be found"

        nominee.position_name = position_name
        nominee.election = election
        nominee.name = full_name
        nominee.speech = speech
        nominee.facebook = facebook_link
        nominee.linked_in = linkedin_link
        nominee.email = email_address
        nominee.discord = discord_username
        nominee.position_name = nominee_index
        return True, nominee, None
    else:
        return True, None, None


def _update_nominee_information_for_existing_election_from_webform(election, updated_elections_information):
    """Updates and saves the nominee for an election that are inputted using the WebForm

    Keyword Arguments
    election -- the election object that needs to be updated
    updated_elections_information -- the POST section of request

    """
    existing_nominees = Nominee.objects.all().filter(nomination_page_id=election.id)
    existing_nominees_names = [existing_nominee.name for existing_nominee in existing_nominees]
    new_nominees_names = []
    full_name = updated_elections_information[NOM_NAME_POST_KEY]
    position_name = updated_elections_information[NOM_POSITIONS_POST_KEY]
    speech = updated_elections_information[NOM_SPEECH_POST_KEY]
    facebook_link = updated_elections_information[NOM_FACEBOOK_POST_KEY]
    linkedin_link = updated_elections_information[NOM_LINKEDIN_POST_KEY]
    email_address = updated_elections_information[NOM_EMAIL_POST_KEY]
    discord_username = updated_elections_information[NOM_DISCORD_USERNAME_POST_KEY]
    if full_name not in existing_nominees_names:
        success, nominee, error_message = _validate_and_return_new_nominee(
            full_name, position_name, speech, facebook_link, linkedin_link, email_address, discord_username, 0
        )
        if success and nominee is not None:
            nominee.election = election
            nominee.save()
            new_nominees_names.append(full_name)
    else:
        success, nominee, error_message = \
            _validate_new_information_for_existing_nominee_for_existing_election_and_return_it(
                election, full_name, position_name, speech, facebook_link, linkedin_link, email_address,
                discord_username, 0
            )
        if success and nominee is not None:
            nominee.election = election
            nominee.save()
            new_nominees_names.append(full_name)
    for existing_nominee in existing_nominees:
        if existing_nominee.name not in new_nominees_names:
            existing_nominee.delete()
