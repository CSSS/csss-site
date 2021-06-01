import datetime
import logging
import os

from django.conf import settings
from django.contrib.staticfiles import finders

from about.models import Term, Officer, AnnouncementEmailAddress, OfficerEmailListAndPositionMapping
from csss.Gmail import Gmail
from csss.settings import ENVIRONMENT, STATIC_ROOT
from resource_management.models import GoogleMailAccountCredentials, NaughtyOfficer, \
    OfficerPositionGithubTeamMapping
from resource_management.views.resource_apis.github.github_api import GitHubAPI

TAB_STRING = 'about'

ELECTION_OFFICER_POSITIONS = ["By-Election Officer", "General Election Officer"]
OFFICER_WITH_NO_ACCESS_TO_CSSS_DIGITAL_RESOURCES = ["SFSS Council-Representative"]
OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE = OFFICER_WITH_NO_ACCESS_TO_CSSS_DIGITAL_RESOURCES.copy()
OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE.extend(ELECTION_OFFICER_POSITIONS.copy())

HTML_VALUE_ATTRIBUTE_FOR_DATE = 'date_value'
HTML_VALUE_ATTRIBUTE_FOR_OVERWRITING_OFFICERS = "overwrite_value"
HTML_VALUE_ATTRIBUTE_FOR_START_DATE = "start_date_value"
logger = logging.getLogger('csss_site')

FIRST_TERM_SEASON = 'Spring'
SECOND_TERM_SEASON = 'Summer'
THIRD_TERM_SEASON = 'Fall'
TERM_SEASONS = [FIRST_TERM_SEASON, SECOND_TERM_SEASON, THIRD_TERM_SEASON]


def _get_position_mappings_assigned_to_specified_positions_names(officer_position_names):
    """
    Returns all officer_mappings that map to the specified position_names

    Keyword Argument
    officer_position_names -- the position_name for the required OfficerEmailListAndPositionMapping object

    Return
    success -- bool to Success, turns false if one of the officer position_names is not valid
    error_message -- error_message if not successful
    officer_position_and_github_mapping -- the OfficerEmailListAndPositionMapping object that maps
     to the specified officer position names
    """
    officer_position_mappings = []
    for officer_position_name in officer_position_names:
        officer_position_mapping = OfficerEmailListAndPositionMapping.objects.all().filter(
            position_name=officer_position_name
        )
        if len(officer_position_mapping) == 0:
            error_message = f"No officer found for position with position_name {officer_position_name}"
            logger.info(
                "[about/officer_management_helper.py "
                f"_get_position_mappings_assigned_to_specified_positions_names()] {error_message}"
            )
            return False, f"{error_message}", None
        officer_position_mappings.append(officer_position_mapping[0])
    logger.info(
        "[about/officer_management_helper.py "
        "_get_position_mappings_assigned_to_specified_positions_names()]"
        f" officer_position_mappings = {officer_position_mappings}"
    )
    return True, None, officer_position_mappings


def get_term_number(year, term_season):
    """
    gets the term number using the year and term

    Keyword Arguments
    year -- the current year in YYYY format
    term_season -- the season that the term takes place in, e.g. Spring, Summer or Fall

    returns the term_number, which is in the format YYYY<1/2/3>, or None if year is not a number
     or specified season does not exist
    """
    return None \
        if ((not f"{year}".isdigit()) or term_season not in TERM_SEASONS) \
        else int(year) * 10 + _get_term_season_number(term_season)


def _get_term_obj_season_number(term_obj):
    """
    Gets the term number using the term object

    Keyword Arguments
    term -- the term object that the function will return its number

    Returns
    term_season_number -- the number of the tem, e.g. 1, 2, or 3. this can also be -1 if the
        term does not have a valid season
    """
    return _get_term_season_number(term_obj.term)


def _get_term_season_number(term_season):
    """
    Gets the term number using the specified season

    Keyword Arguments
    term -- the term object that the function will return its number

    Returns
    term_season_number -- the number of the tem, e.g. 1, 2, or 3. this can also be None if the
        term does not have a valid season
    """
    if term_season == FIRST_TERM_SEASON:
        return 1
    elif term_season == SECOND_TERM_SEASON:
        return 2
    elif term_season == THIRD_TERM_SEASON:
        return 3
    return None


def save_new_term(year, term_season):
    """
    either saves a new term with the given year and term or just returns an existing term that matches that given
    year and term

    Keyword Arguments
    year -- the year in YYYY format
    term -- the season that the term takes place in, e.g. Spring, Summer or Fall

    Return
    term_obj -- the term object that corresponds to given year and term
     or None if proper term year and season not specified
    """
    term_number = get_term_number(year, term_season)
    if term_number is None:
        return None
    term_obj, created = Term.objects.get_or_create(
        term=term_season,
        term_number=term_number,
        year=int(year)
    )
    return term_obj


def save_officer_and_grant_digital_resources(phone_number, full_name, sfuid, sfu_email_alias,
                                             announcement_emails, github_username, gmail, start_date, fav_course_1,
                                             fav_course_2, fav_language_1, fav_language_2, bio, position_name,
                                             position_index, term_obj, sfu_officer_mailing_list_email,
                                             remove_from_naughty_list=False,
                                             apply_github_team_memberships=True,
                                             gdrive_api=None, gitlab_api=None,
                                             send_email_notification=False):
    """
    Saves the officer with all the necessary info and gives them access to digital resources
     if flags indicate that they should be given access

    Keyword Argument
    phone_number -- officer's phone number
    full_name -- the officer's full name
    sfuid -- the officer's SFUID
    sfu_email_alias -- the officer's sfu email alias
    announcement_emails -- all the emails that the officer may use for sending out SFU CSSS emails to the students
    github_username -- the officer's github username
    gmail -- the officer's gmail
    start_date -- the date that the officer started their current term of their position
    fav_course_1 -- the officer's first fav course
    fav_course_2 -- the officer's second fav course
    fav_language_1 -- the officer's first fav language
    fav_language_2 -- the officer's second fav language
    bio -- the officer's bio that is already in html markdown form
    position_name -- the name for the officer's position
    position_index -- the index for the officer's position
    term_obj -- the term that the officer's info is being saved for
    sfu_officer_mailing_list_email -- the sfu email list that the officer will be contact-able at
    remove_from_naughty_list -- indicates whether or not to remove the officer from the list
     that determines whether or not to keep their name in the list that prevents them from
     gaining access to CSSS resources
    apply_github_team_memberships -- indicates whether or not the officer needs to be given github access
    gdrive_api -- the google drive object that is used to communicate with the google drive API
    gitlab_api -- the SFU gitlab object that is used to communicate with the SFU gitlab API
    send_email_notifications -- indicates whether or not to send an email to the officer's SFU email with instruction

    Returns
    success - true or False
    error_message -- error message if success is False
    """

    pic_path = get_officer_image_path(term_obj, full_name)
    logger.info(
        f"[about/officer_management_helper.py save_officer_and_grant_digital_resources()] pic_path set to {pic_path}")

    if type(start_date) != datetime.datetime:
        # if taking in the start_date from the form that the new officers have to fill in
        start_date = datetime.datetime.strptime(start_date, "%A, %d %b %Y %I:%m %S %p")

    officer_obj = Officer(position_name=position_name, position_index=position_index, name=full_name,
                          sfuid=sfuid, sfu_email_alias=sfu_email_alias, phone_number=phone_number,
                          github_username=github_username, gmail=gmail, course1=fav_course_1,
                          course2=fav_course_2, language1=fav_language_1, language2=fav_language_2, bio=bio,
                          image=pic_path, elected_term=term_obj,
                          sfu_officer_mailing_list_email=sfu_officer_mailing_list_email, start_date=start_date)

    logger.info(
        "[about/officer_management_helper.py save_officer_and_grant_digital_resources()] "
        f"saved user term={term_obj} full_name={full_name} position_name={position_name}"
    )

    officer_obj.save()

    for email in announcement_emails:
        AnnouncementEmailAddress(email=email, officer=officer_obj).save()

    if position_name not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
        if gdrive_api is not None:
            logger.info(
                "[about/officer_management_helper.py save_officer_and_grant_digital_resources()] "
                f"giving user {officer_obj} access to CSSS google drive"
            )
            success, file_name, error_message = gdrive_api.add_users_gdrive([gmail])
            if not success:
                officer_obj.delete()
                return success, error_message
        if gitlab_api is not None:
            logger.info(
                "[about/officer_management_helper.py save_officer_and_grant_digital_resources()] "
                f"giving user {officer_obj} access to SFU CSSS Gitlab"
            )
            success, error_message = gitlab_api.add_officer_to_csss_group([sfuid])
            if not success:
                officer_obj.delete()
                return success, error_message

    if apply_github_team_memberships:
        success, error_message = _save_officer_github_membership(officer_obj)
        if not success:
            officer_obj.delete()
            return success, error_message
    subject = "Welcome to the CSSS"
    body = None
    if send_email_notification:
        logger.info(
            "[about/officer_management_helper.py save_officer_and_grant_digital_resources()] "
            f"sending email notification to user {officer_obj} who is in the officer position {position_name}"
        )
        if position_name not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
            body = (
                f"Hello {full_name},\n\n"
                "Congrats on becoming a CSSS Officer,\n\n"
                "Please make sure that you\n\n"
                " 1. check the email associated with your github for an invitation to our SFU CSSS Github org on "
                "Github\n "
                " 2. check your sfu email for an invitation to join our SFU CSSS org on SFU Gitlab\n\n"
                "Apart from that, take the following documentation, which is linked here, as it is a "
                "nightmare trying to figure out "
                "markdown for gmail from a python script: https://github.com/CSSS/documents/wiki"
            )
        elif position_name in ELECTION_OFFICER_POSITIONS:
            body = (
                f"Hello {full_name},\n\n"
                "Congrats on becoming a CSSS Election Officer,\n\n"
                "Please read the following documentation, which is linked here, "
                "as it is a nightmare trying to figure out "
                "markdown for gmail from a python script: https://github.com/CSSS/elections-documentation"
            )
        if body is not None:
            # only sending an email if the new officer got a body which only happens if the user was granted access
            # to any csss digital resources
            gmail_credentials = GoogleMailAccountCredentials.objects.all().filter(username="sfucsss@gmail.com")
            if len(gmail_credentials) == 0:
                officer_obj.delete()
                return False, ("Could not find any credentials for the gmail sfucsss@gmail.com account "
                               "in order to send notification email")
            sfu_csss_credentials = gmail_credentials[0]
            gmail = Gmail(sfu_csss_credentials.username, sfu_csss_credentials.password)
            if not gmail.connection_successful:
                return False, gmail.error_message
            success, error_message = gmail.send_email(
                subject, body, f"{sfuid}@sfu.ca", full_name, "SFU CSSS Website"
            )
            if not success:
                return False, error_message
            success, error_message = gmail.close_connection()
            if not success:
                officer_obj.delete()
                return success, error_message
    if remove_from_naughty_list:
        _remove_officer_from_naughty_list(sfuid)
    return True, None


def get_officer_image_path(term_obj, full_name):
    """
    determines what the image path for the officer should be

    Keyword Argument
    term_obj -- the term for the officer
    full_name -- the officer's full name

    Return
    pic_path -- the path for the officer's image
    """
    valid_picture_extensions = ['jpg', 'jpeg','png']
    valid_picture_path = None
    if ENVIRONMENT == "LOCALHOST":
        for valid_picture_extension in valid_picture_extensions:
            if valid_picture_path is None or valid_picture_path == "stockPhoto.jpg":
                term_season_number = _get_term_obj_season_number(term_obj)
                if term_season_number is None:
                    valid_picture_path = "stockPhoto.jpg"
                else:
                    pic_path = (f'{term_obj.year}_0{term_season_number}_'
                                f'{term_obj.term}/{full_name.replace(" ", "_")}.{valid_picture_extension}')
                    full_path = finders.find(pic_path)
                    logger.info("[about/officer_management_helper.py get_officer_image_path()] "
                                f"full_path = {full_path}")
                    if full_path is None or not os.path.isfile(full_path):
                        valid_picture_path = "stockPhoto.jpg"
                    else:
                        valid_picture_path = pic_path
    else:
        path_prefix = "about_static/exec-photos/"
        logger.info(f"[about/officer_management_helper.py get_officer_image_path()] "
                    f"path_prefix = {path_prefix}")
        for valid_picture_extension in valid_picture_extensions:
            if valid_picture_path is None or valid_picture_path == f"{path_prefix}stockPhoto.jpg":
                term_season_number = _get_term_obj_season_number(term_obj)
                if term_season_number is None:
                    valid_picture_path = f"{path_prefix}stockPhoto.jpg"
                else:
                    pic_path = (f'{term_obj.year}_0{_get_term_obj_season_number(term_obj)}_'
                                f'{term_obj.term}/{full_name.replace(" ", "_")}.{valid_picture_extension}')
                    pic_path = f"{path_prefix}{pic_path}"
                    logger.info(f"[about/officer_management_helper.py get_officer_image_path()] "
                                f"officer.image = {pic_path}")
                    absolute_path = f"{STATIC_ROOT}{pic_path}"
                    logger.info(f"[about/officer_management_helper.py get_officer_image_path()] "
                                f"absolute_path = {absolute_path}")
                    if not os.path.isfile(absolute_path):
                        valid_picture_path = f"{path_prefix}stockPhoto.jpg"
                    else:
                        valid_picture_path = pic_path
    logger.info("[about/officer_management_helper.py get_officer_image_path()] "
                f"image set to = '{valid_picture_path}'")
    return valid_picture_path


def _save_officer_github_membership(officer):
    """
    Adds the officers to the necessary github teams.

    Keyword Arguments
    officer -- the officer to add to the github teams

    return
    success -- true or false Bool
    error_message -- the error_message if success is False or None otherwise
    """
    position_mapping = OfficerEmailListAndPositionMapping.objects.all().filter(
        position_index=officer.position_index
    )
    if len(position_mapping) == 0:
        error_message = f"could not find any position mappings for position_index {officer.position_index}"
        logger.info(f"[about/officer_management_helper.py _save_officer_github_membership()] {error_message}")
        return False, error_message

    github_api = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
    if github_api.connection_successful is False:
        logger.info("[about/officer_management_helper.py _save_officer_github_membership()]"
                    f" {github_api.error_message}")
        return False, f"{github_api.error_message}"
    github_team_mappings = OfficerPositionGithubTeamMapping.objects.all().filter(
        officer_position_mapping=position_mapping[0]
    )
    for github_team_mapping in github_team_mappings:
        success, error_message = github_api.add_users_to_a_team(
            [officer.github_username],
            github_team_mapping.github_team.team_name
        )
        if not success:
            logger.info(
                "[about/officer_management_helper.py _save_officer_github_membership()] "
                f"unable to add officer {officer.github_username} to team"
                f" {github_team_mapping.github_team.team_name} due to error {error_message}"
            )
            return False, error_message
        logger.info(
            "[about/officer_management_helper.py _save_officer_github_membership()] "
            f"mapped officer {officer} to team {github_team_mapping.github_team.team_name}"
        )
    return True, None


def _remove_officer_from_naughty_list(sfuid):
    """
    Removes the office form the naughty list so that their permissions remain
    even after a validation

    Keyword Argument
    sfuid -- the sfuid of the officer
    """
    logger.info(f"[about/officer_management_helper.py _remove_officer_from_naughty_list()] sfuid: [{sfuid}]")
    naughty_officers = NaughtyOfficer.objects.all()
    for naughty_officer in naughty_officers:
        logger.info(
            "[about/officer_management_helper.py _remove_officer_from_naughty_list()] will compare sfuid"
            f" [{sfuid}] with naughty_officer.sfuid [{naughty_officer.sfuid}]"
        )
        if naughty_officer.sfuid == sfuid:
            logger.info(
                f"[about/officer_management_helper.py _remove_officer_from_naughty_list()] deleting "
                f"naughty_officer {naughty_officer.sfuid}"
            )
            naughty_officer.delete()
            return
