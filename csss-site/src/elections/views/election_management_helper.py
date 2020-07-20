import datetime
import logging


from elections.models import NominationPage, Nominee
from elections.views.election_management import NOM_NAME_POST_KEY, NOM_POSITION_POST_KEY, NOM_SPEECH_POST_KEY, \
    NOM_FACEBOOK_POST_KEY, NOM_LINKEDIN_POST_KEY, NOM_EMAIL_POST_KEY, NOM_DISCORD_USERNAME_POST_KEY, \
    ELECTION_DATE_POST_KEY, ELECTION_TYPE_KEY, ELECTION_DATE_KEY, ELECTION_WEBSURVEY_LINK_KEY, \
    ELECTION_NOMINEES_KEY, NOM_FACEBOOK_KEY, NOM_NAME_KEY, NOM_SPEECH_KEY, NOM_POSITION_KEY, \
    NOM_DISCORD_USERNAME_KEY, NOM_EMAIL_KEY, NOM_LINKEDIN_KEY, ELECTION_TIME_POST_KEY, ELECTION_TYPE_POST_KEY, \
    ELECTION_WEBSURVEY_LINK_POST_KEY

logger = logging.getLogger('csss_site')


def _create_new_election_from_webform(updated_elections_information):
    """Extracts the date from the election_dict and passes it off to create_new_nomination_page to create
    the election object before it is passed back to this function and saved

    Keyword Argument
    updated_elections_information -- the POST section of request

    Return
    nomination_page -- the saved election object
    """
    dt = datetime.datetime.strptime(
        f"{updated_elections_information[ELECTION_DATE_POST_KEY]} "
        f"{updated_elections_information[ELECTION_TIME_POST_KEY]}",
        '%Y-%m-%d %H:%M'
    )
    success, election_page, error_message = \
        _validate_and_return_information_from_new_election(dt,
                                                           updated_elections_information
                                                           )
    election_page.save()
    logger.info(
        "[elections/election_management.py _create_new_election_from_webform()] nomination_page "
        f"{election_page} created with slug {election_page.slug}, election_type={election_page.election_type}, "
        f"date={election_page.date}, websurvey={election_page.websurvey}, "
        f"human_friendly_name={election_page.human_friendly_name} "
    )
    return election_page


def _validate_and_return_information_from_new_election(dt, updated_elections_information):
    """extract all the information for the election [excluding the datetime] and passes it off to
    save_new_election_to_db to create the election object before returning it back

    Keyword Argument
    dt -- the datetime representation for the election's date
    updated_elections_information -- the POST section of request

    Return
    Boolean -- true if election was saved and false if it was not
    nomination_page -- the election object, if one was created
    error_message -- populated if the election could not be saved
    """
    valid_election_type_choices = [election_type_choice[0] for election_type_choice in
                                   NominationPage.election_type_choices]
    election_type = updated_elections_information[ELECTION_TYPE_POST_KEY]
    if election_type not in valid_election_type_choices:
        logger.error(
            f"[elections/election_management.py _validate_and_return_information_from_new_election()] given "
            f"election_type of {election_type} is not one of the valid options {valid_election_type_choices}"
        )
        return False, None, f"the election type you entered {election_type} needs to be one of the following " \
                            f"values: {valid_election_type_choices}"
    election_websurvey = updated_elections_information[ELECTION_WEBSURVEY_LINK_POST_KEY]
    slug, human_friendly_name = _create_slug_and_human_friendly_name_election(dt, election_type)
    return True, _create_election_object(election_type, election_websurvey, dt, slug, human_friendly_name), None


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
                                    for valid_election_type_choice in NominationPage.election_type_choices
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
    return NominationPage(slug=slug, election_type=election_type, date=dt,
                          websurvey=election_websurvey, human_friendly_name=human_friendly_name)


def _save_nominees_for_new_election_from_webform(election, updated_elections_information):
    """takes in a list of nominees' information and save them as nominee objects

    Keyword Arguments
    election -- the election object that the new nominees belong to
    updated_elections_information -- the POST section of request
    """
    for nominee_index in range(len(updated_elections_information[NOM_NAME_POST_KEY])):
        success, nominee, error_message = _validate_and_return_new_nominee(
            updated_elections_information[NOM_NAME_POST_KEY][nominee_index],
            updated_elections_information[NOM_POSITION_POST_KEY][nominee_index],
            updated_elections_information[NOM_SPEECH_POST_KEY][nominee_index],
            updated_elections_information[NOM_FACEBOOK_POST_KEY][nominee_index],
            updated_elections_information[NOM_LINKEDIN_POST_KEY][nominee_index],
            updated_elections_information[NOM_EMAIL_POST_KEY][nominee_index],
            updated_elections_information[NOM_DISCORD_USERNAME_POST_KEY][nominee_index], nominee_index
        )
        if nominee is not None:
            nominee.nomination_page = election
            nominee.save()


def _validate_and_return_new_nominee(full_name, officer_position, speech, facebook_link, linkedin_link,
                                     email_address, discord_username, nominee_index):
    """Takes in the info of a single nominee [except its election] and creates the nominee object
    that will need to be saved

    Keyword Arguments
    full_name -- the full name of the nominee
    officer_position -- the officer position the nominee is running for
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
    if len(officer_position.strip()) == 0:
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
    if full_name != 'NONE':  # if full_name is NONE, then it is a nominee that needs to be removed
        return True, Nominee(name=full_name, officer_position=officer_position,
                             speech=speech,
                             facebook=facebook_link, linked_in=linkedin_link, email=email_address,
                             discord=discord_username,
                             position=nominee_index
                             ), None
    return True, None, None


def _validate_and_return_information_for_new_election_from_json(updated_elections_information):
    """Extracts the date from the election_dict and passes it off to create_new_nomination_page
    to create the election object

    Keyword Argument
    updated_elections_information -- the POST section of request

    Return
    Boolean -- true if election was saved and false if it was not
    nomination_page -- the election object, if one was created
    error_message -- populated if the election could not be saved
    """
    try:
        dt = datetime.datetime.strptime(f"{updated_elections_information[ELECTION_DATE_POST_KEY]}", '%Y-%m-%d %H:%M')
    except ValueError:
        logger.error(
            "[elections/election_management.py _validate_and_return_information_for_new_election_from_json()]"
            f" given date of {updated_elections_information[ELECTION_DATE_POST_KEY]} is not in the valid format "
            "of YYYY-MM-DD HH:MM"
        )
        return False, None, f"the date you entered {updated_elections_information[ELECTION_DATE_POST_KEY]} " \
                            "is not in a valid format of \"YYYY-MM-DD HH:MM\""
    except TypeError:
        logger.error(
            "[elections/election_management.py _validate_and_return_information_for_new_election_from_json()] "
            "given date seems to be unreadable"
        )
        return False, None, "the date you entered seems to be unreadable"
    return _validate_and_return_information_from_new_election(dt, updated_elections_information)


def _validate_new_nominees_for_new_election_from_json(nominees):
    """takes in a list of nominees to save under the given nomination page from the json page

    Keyword Arguments
    nominees -- a dictionary that contains a list of all the nominees to save under specified nomination_page

    Return
    Boolean -- true if election was saved and false if it was not
    nominees -- list of nominees that need to be saved
    error_message -- populated if the nominee[s] could not be saved
    """
    nominee_index = 0
    nominees_to_save = []
    for nominee in nominees:
        if NOM_NAME_POST_KEY in nominee and NOM_POSITION_POST_KEY in nominee and NOM_SPEECH_POST_KEY in nominee and \
                NOM_FACEBOOK_POST_KEY in nominee and NOM_LINKEDIN_POST_KEY in nominee and \
                NOM_EMAIL_POST_KEY in nominee and NOM_DISCORD_USERNAME_POST_KEY in nominee:
            success, nominee, error_message = _validate_and_return_new_nominee(
                nominee[NOM_NAME_POST_KEY], nominee[NOM_POSITION_POST_KEY],
                nominee[NOM_SPEECH_POST_KEY], nominee[NOM_FACEBOOK_POST_KEY],
                nominee[NOM_LINKEDIN_POST_KEY], nominee[NOM_EMAIL_POST_KEY],
                nominee[NOM_DISCORD_USERNAME_POST_KEY], nominee_index
            )
            if success:
                if nominee is not None:
                    nominees_to_save.append(nominee)
                    nominee_index += 1
            else:
                return False, None, error_message

        else:
            return False, None, "It seems that one of the nominees is missing a field"
    return True, nominees_to_save, None


def _get_information_for_election_user_wants_to_modify(election_id):
    """Returns information about the election

    Keyword Argument
    election_id -- the id for the election to get information about

    Return
    election_dictionary -- a JSON representation of the election information and its list of nominees
    """
    election = NominationPage.objects.get(id=election_id)
    nominees = [nominee for nominee in Nominee.objects.all().filter(nomination_page=election)]
    nominees.sort(key=lambda x: x.position, reverse=True)
    election_dictionary = {ELECTION_TYPE_KEY: election.election_type,
                           ELECTION_DATE_KEY: election.date.strftime("%Y-%m-%d %H:%M"),
                           ELECTION_WEBSURVEY_LINK_KEY: election.websurvey, ELECTION_NOMINEES_KEY: []}
    for nominee in nominees:
        election_dictionary[ELECTION_NOMINEES_KEY].append(
            {NOM_NAME_KEY: nominee.name, NOM_EMAIL_KEY: nominee.email, NOM_LINKEDIN_KEY: nominee.linked_in,
             NOM_FACEBOOK_KEY: nominee.facebook, NOM_DISCORD_USERNAME_KEY: nominee.discord,
             NOM_SPEECH_KEY: nominee.speech, NOM_POSITION_KEY: nominee.officer_position})

    return election_dictionary


def _get_existing_election_by_id(election_id):
    """Returns an election page by id

    Keyword Argument
    election_id -- the id for the election to return

    Return
    nom_pages -- the election object for the election the user wants
    """
    try:
        nom_pages = NominationPage.objects.get(id=election_id)
    except NominationPage.DoesNotExist:
        logger.info("[elections/election_management.py _get_existing_election_by_id()] unable to find an election by "
                    f"id {election_id}")
        return None
    return nom_pages


def _validate_information_for_existing_election_from_webform_and_return_it(nomination_page,
                                                                           updated_elections_information):
    """Extracts the date from the election_dict and passes it off to the next function to update the election page
    before returning the created nomination page that still needs to be saved

    Keyword Argument
    nomination_page -- the election object that needs to be updated
    updated_elections_information -- the POST section of request that contains the new information

    Return
    nomination_page -- the election object, if it existed. otherwise None
    """
    dt = datetime.datetime.strptime(
        f"{updated_elections_information[ELECTION_DATE_POST_KEY]} "
        f"{updated_elections_information[ELECTION_TIME_POST_KEY]}",
        '%Y-%m-%d %H:%M')
    success, nomination_page, error_message = \
        _validate_information_for_existing_election_obj_and_return_it(dt,
                                                                      nomination_page,
                                                                      updated_elections_information)
    return nomination_page


def _validate_information_for_existing_election_obj_and_return_it(dt, nomination_page, updated_elections_information):
    """extracts all the information for the election [excluding the datetime] and creates the election object
    that still needs to be saved

    Keyword Argument
    dt -- the datetime representation for the elections's date
    nomination_page -- the election objet that needs to be updated
    updated_elections_information -- the POST section of request

    Return
    Boolean -- true if election had been saved and false if it was not
    nomination_page -- the election object, if one was created
    error_message -- populated if the election could not be saved
    """
    valid_election_type_choices = [election_type_choice[0] for election_type_choice in
                                   NominationPage.election_type_choices]
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
    slug, human_friendly_name = _create_slug_and_human_friendly_name_election(dt, chosen_election_type)
    nomination_page.slug = slug
    nomination_page.human_friendly_name = human_friendly_name
    nomination_page.election_type = chosen_election_type
    nomination_page.date = dt
    nomination_page.websurvey = election_websurvey
    return True, nomination_page, None


def _validate_nominees_information_for_existing_election_from_webform_and_return_them(nomination_page,
                                                                                      updated_elections_information):
    """Updates the nominees for an election that are inputted using the WebForm

    Keyword Arguments
    nomination_page -- the election object that needs to be updated
    updated_elections_information -- the POST section of request
    """
    position_index = 0
    existing_nominees = Nominee.objects.all().filter(nomination_page_id=nomination_page.id)
    existing_nominees_names = [existing_nominee.name for existing_nominee in existing_nominees]
    new_nominees_names = []
    for nominee_index in range(len(updated_elections_information[NOM_NAME_POST_KEY])):
        full_name = updated_elections_information[NOM_NAME_POST_KEY][nominee_index]
        officer_position = updated_elections_information[NOM_POSITION_POST_KEY][nominee_index]
        speech = updated_elections_information[NOM_SPEECH_POST_KEY][nominee_index]
        facebook_link = updated_elections_information[NOM_FACEBOOK_POST_KEY][nominee_index]
        linkedin_link = updated_elections_information[NOM_LINKEDIN_POST_KEY][nominee_index]
        email_address = updated_elections_information[NOM_EMAIL_POST_KEY][nominee_index]
        discord_username = updated_elections_information[NOM_DISCORD_USERNAME_POST_KEY][nominee_index]
        if full_name not in existing_nominees_names:
            success, nominee, error_message = \
                _validate_and_return_new_nominee(
                    full_name, officer_position, speech, facebook_link, linkedin_link,
                    email_address, discord_username, position_index
                )
            if success and nominee is not None:
                nominee.nomination_page = nomination_page
                nominee.save()
                logger.info(
                    "[elections/election_management.py _validate_nominees_information_for_existing_election_from"
                    f"_webform_and_return_them()] saved user full_name={full_name} "
                    f"officer_position={officer_position}"
                    f" facebook_link={facebook_link} linkedin_link={linkedin_link} "
                    f"email_address={email_address} discord_username={discord_username}"
                )
                new_nominees_names.append(full_name)
                position_index += 1
        else:
            success, nominee, error_message = \
                _validate_new_information_for_existing_nominee_for_existing_election_and_return_it(
                    nomination_page, full_name, officer_position, speech, facebook_link, linkedin_link, email_address,
                    discord_username, position_index
                )
            if success and nominee is not None:
                nominee.save()
                logger.info(
                    "[elections/election_management.py _validate_nominees_information_for_existing_"
                    "election_from_webform_and_return_them()] updated user "
                    f"full_name={full_name} officer_position={officer_position}"
                    f" facebook_link={facebook_link} linkedin_link={linkedin_link} "
                    f"email_address={email_address} discord_username={discord_username}"
                )
                new_nominees_names.append(full_name)
                position_index += 1
    for existing_nominee in existing_nominees:
        if existing_nominee.name not in new_nominees_names:
            existing_nominee.delete()


def _validate_new_information_for_existing_nominee_for_existing_election_and_return_it(
        nomination_page, full_name, officer_position, speech, facebook_link, linkedin_link, email_address,
        discord_username, nominee_index):
    """Takes in the info of a single nominee to save it under given nomination page

    Keyword Arguments
    nomination_page -- the nomination page to save the nominee under
    full_name -- the full name of the nominee
    officer_position -- the officer position the nominee is running for
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
        if len(officer_position.strip()) == 0:
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
            nominee = Nominee.objects.get(nomination_page=nomination_page, name=full_name,
                                          officer_position=officer_position)
        except Nominee.DoesNotExist:
            logger.info(
                "[elections/election_management.py _validate_new_information_for_existing_nominee_for_e"
                "xisting_election_and_return_it()] unable to find "
                f"nominee full_name={full_name} officer_position={officer_position} for election {nomination_page}"
            )
            return False, None, f"The nominee {full_name} for position {officer_position} could not be found"

        nominee.officer_position = officer_position
        nominee.nomination_page = nomination_page
        nominee.name = full_name
        nominee.speech = speech
        nominee.facebook = facebook_link
        nominee.linked_in = linkedin_link
        nominee.email = email_address
        nominee.discord = discord_username
        nominee.position = nominee_index
        return True, nominee, None
    else:
        return True, None, None


def _update_nominee_information_for_existing_election_from_webform(nomination_page, updated_elections_information):
    """Updates and saves the nominee for an election that are inputted using the WebForm

    Keyword Arguments
    nomination_page -- the election object that needs to be updated
    updated_elections_information -- the POST section of request

    """
    existing_nominees = Nominee.objects.all().filter(nomination_page_id=nomination_page.id)
    existing_nominees_names = [existing_nominee.name for existing_nominee in existing_nominees]
    new_nominees_names = []
    full_name = updated_elections_information[NOM_NAME_POST_KEY]
    officer_position = updated_elections_information[NOM_POSITION_POST_KEY]
    speech = updated_elections_information[NOM_SPEECH_POST_KEY]
    facebook_link = updated_elections_information[NOM_FACEBOOK_POST_KEY]
    linkedin_link = updated_elections_information[NOM_LINKEDIN_POST_KEY]
    email_address = updated_elections_information[NOM_EMAIL_POST_KEY]
    discord_username = updated_elections_information[NOM_DISCORD_USERNAME_POST_KEY]
    if full_name not in existing_nominees_names:
        success, nominee, error_message = _validate_and_return_new_nominee(
            full_name, officer_position, speech, facebook_link, linkedin_link, email_address, discord_username, 0
        )
        if success and nominee is not None:
            nominee.nomination_page = nomination_page
            nominee.save()
            new_nominees_names.append(full_name)
    else:
        success, nominee, error_message = \
            _validate_new_information_for_existing_nominee_for_existing_election_and_return_it(
                nomination_page, full_name, officer_position, speech, facebook_link, linkedin_link, email_address,
                discord_username, 0
            )
        if success and nominee is not None:
            nominee.nomination_page = nomination_page
            nominee.save()
            new_nominees_names.append(full_name)
    for existing_nominee in existing_nominees:
        if existing_nominee.name not in new_nominees_names:
            existing_nominee.delete()


def _update_information_for_existing_election_from_json(nomination_page, updated_elections_information):
    """extracts the data from the election_dict and passes it off to update_election_obj to update the election object

    Keyword Argument
    nomination_page -- the election object that needs to be updated
    updated_elections_information -- the POST section of request


    Return
    Boolean -- true if election was saved and false if it was not
    nomination_page -- the election object, if one was created
    error_message -- populated if the election could not be saved
    """
    try:
        dt = datetime.datetime.strptime(f"{updated_elections_information[ELECTION_DATE_POST_KEY]}", '%Y-%m-%d %H:%M')
    except ValueError:
        logger.error(
            "[elections/election_management.py _update_information_for_existing_election_from_json()] given "
            f"date of {updated_elections_information[ELECTION_DATE_POST_KEY]} is not"
            " in the valid format of YYYY-MM-DD HH:MM")
        return False, None, f"the date you entered {updated_elections_information[ELECTION_DATE_POST_KEY]} " \
                            "is not in a valid format of \"YYYY-MM-DD HH:MM\""
    except TypeError:
        logger.error(
            "[elections/election_management.py _create_new_election_from_json()] given date seems to be unreadable")
        return False, None, "the date you entered seems to be unreadable "
    return _validate_information_for_existing_election_obj_and_return_it(dt, nomination_page,
                                                                         updated_elections_information)


def _validate_nominee_information_for_existing_elections_from_json_and_save_all_changes(nomination_page,
                                                                                        updated_nominees_information):
    """Takes in the election object and list of nominees that new to be created under it
    will then validate all the updated nominees to ensure they are all correct. After they are all validated, if they
    all passed the validation, it will then save the updated nomination page object as well as all the
    updated nominees while also deleting any outdated nominees. Otherwise, it will return an error explaining
    why it could not do so.

    Keyword Argument
    nomination_page -- the election object that needs to be updated
    updated_elections_information -- the POST section of request that contains the nominees

    Return
    Boolean -- true if election was saved and false if it was not
    error_message -- populated if the nominee[s] could not be saved
    """
    position_index = 0
    existing_nominees = Nominee.objects.all().filter(nomination_page_id=nomination_page.id)
    existing_nominees_names = [existing_nominee.name for existing_nominee in existing_nominees]
    new_nominees_names = []
    nominees_to_save = []
    for nominee in updated_nominees_information:
        if NOM_NAME_POST_KEY in nominee and NOM_POSITION_POST_KEY in nominee and NOM_SPEECH_POST_KEY in nominee and \
                NOM_FACEBOOK_POST_KEY in nominee and NOM_LINKEDIN_POST_KEY in nominee and \
                NOM_EMAIL_POST_KEY in nominee and NOM_DISCORD_USERNAME_POST_KEY in nominee:
            full_name = nominee[NOM_NAME_POST_KEY]
            officer_position = nominee[NOM_POSITION_POST_KEY]
            speech = nominee[NOM_SPEECH_POST_KEY]
            facebook_link = nominee[NOM_FACEBOOK_POST_KEY]
            linkedin_link = nominee[NOM_LINKEDIN_POST_KEY]
            email_address = nominee[NOM_EMAIL_POST_KEY]
            discord_username = nominee[NOM_DISCORD_USERNAME_POST_KEY]
            if full_name not in existing_nominees_names:
                success, nominee, error_message = \
                    _validate_and_return_new_nominee(full_name, officer_position, speech,
                                                     facebook_link, linkedin_link,
                                                     email_address, discord_username,
                                                     position_index)
                if success:
                    if nominee is not None:
                        nominees_to_save.append(nominee)
                        new_nominees_names.append(full_name)
                        position_index += 1
                else:
                    return False, error_message
            else:
                success, nominee, error_message = \
                    _validate_new_information_for_existing_nominee_for_existing_election_and_return_it(
                        nomination_page, full_name, officer_position, speech, facebook_link, linkedin_link,
                        email_address, discord_username, position_index)
            if success:
                if nominee is not None:
                    nominees_to_save.append(nominee)
                    new_nominees_names.append(full_name)
                    position_index += 1
            else:
                return False, error_message

    nomination_page.save()
    for existing_nominee in existing_nominees:
        if existing_nominee.name not in new_nominees_names:
            existing_nominee.delete()
    for nominee in nominees_to_save:
        nominee.nomination_page = nomination_page
        nominee.save()
    return True, None
