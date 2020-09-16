import datetime
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from about.models import Term, Officer, AnnouncementEmailAddress
from resource_management.models import GoogleMailAccountCredentials, NaughtyOfficer, OfficerGithubTeamMapping, \
    OfficerGithubTeam

TAB_STRING = 'about'

GITHUB_OFFICER_TEAM = "officers"

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


def get_term_number(year, term_season):
    """
    gets the term number using the year and term

    Keyword Arguments
    year -- the current year in YYYY format
    term_season -- the season that the term takes place in, e.g. Spring, Summer or Fall

    returns the term_number, which is in the format YYYY<1/2/3>

    """
    if term_season == FIRST_TERM_SEASON:
        return int(year) * 10 + 1
    elif term_season == SECOND_TERM_SEASON:
        return int(year) * 10 + 2
    elif term_season == THIRD_TERM_SEASON:
        return int(year) * 10 + 3


def save_new_term(year, term):
    """
    either saves a new term with the given year and term or just returns an existing term that matches that given
    year and term

    Keyword Arguments
    year -- the year in YYYY format
    term -- the season that the term takes place in, e.g. Spring, Summer or Fall

    Return
    term_obj -- the term objet that corresponds to given year and term
    """
    term_number = get_term_number(year, term)
    term_obj, created = Term.objects.get_or_create(
        term=term,
        term_number=term_number,
        year=int(year)
    )
    return term_obj


def save_officer_and_grant_digital_resources(phone_number, officer_position, full_name, sfuid, sfu_email_alias,
                                             announcement_emails, github_username, gmail, start_date, fav_course_1,
                                             fav_course_2, fav_language_1, fav_language_2, bio, position_index,
                                             term_obj, sfu_officer_mailing_list_email, remove_from_naughty_list=False,
                                             github_teams=None, github_api=None, gdrive_api=None, gitlab_api=None,
                                             send_email_notification=False):
    """
    Saves the officer with all the necessary info and gives them access to digital resources
     if flags indicate that they should be given access

    Keyword Argument
    phone_number -- officer's phone number
    officer_position -- the officer position being saved
    full_name -- the officer's full name
    sfuid -- the officer's SFUID
    announcement_emails -- all the emails that the officer may use for sending out SFU CSSS emails to the students
    github_username -- the officer's github username
    gmail -- the officer's gmail
    start_date -- the date that the officer started their current term of their position
    fav_course_1 -- the officer's first fav course
    fav_course_2 -- the officer's second fav course
    fav_language_1 -- the officer's first fav language
    fav_language_2 -- the officer's second fav language
    bio -- the officer's bio that is already in html markdown form
    position_index -- the index for the officer's position
    term_obj -- the term that the officer's info is being saved for
    sfu_officer_mailing_list_email -- the sfu email list that the officer will be contact-able at
    remove_from_naughty_list -- indicates whether or not to remove the officer from the list
     that determines whether or not to keep their name in the list that prevents them from
     gaining access to CSSS resources
    github_teams -- the specific teams that the officer should be added to. This has higher
     priority than any other designation if specified
    github_api -- the github object that is used to communicate with github API
    gdrive_api -- the google drive object that is used to communicate with the google drive API
    gitlab_api -- the SFU gitlab object that is used to communicate with the SFU gitlab API
    send_email_notifications -- indicates whether or not to send an email to the officer's SFU email with instruction

    Returns
    success - true or False
    error_message -- error message if success is False
    """

    pic_path = (f'{term_obj.year}_0{_get_term_season_number(term_obj)}_'
                f'{term_obj.term}/{full_name.replace(" ", "_")}.jpg')
    logger.info(
        f"[about/officer_management_helper.py save_officer_and_grant_digital_resources()] pic_path set to {pic_path}")

    if type(start_date) != datetime.datetime:
        # if taking in the start_date from the form that the new officers have to fill in
        start_date = datetime.datetime.strptime(start_date, "%A, %d %b %Y %I:%m %S %p")

    officer_obj = Officer(position=officer_position, term_position_number=position_index, name=full_name,
                          sfuid=sfuid, sfu_email_alias=sfu_email_alias, phone_number=phone_number,
                          github_username=github_username, gmail=gmail, course1=fav_course_1,
                          course2=fav_course_2, language1=fav_language_1, language2=fav_language_2, bio=bio,
                          image=pic_path, elected_term=term_obj,
                          sfu_officer_mailing_list_email=sfu_officer_mailing_list_email, start_date=start_date)

    logger.info(
        "[about/officer_management_helper.py save_officer_and_grant_digital_resources()] "
        f"saved user term={term_obj} full_name={full_name} officer_position={officer_position}"
    )

    officer_obj.save()

    for email in announcement_emails:
        AnnouncementEmailAddress(email=email, officer=officer_obj).save()

    if officer_position not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
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
    if remove_from_naughty_list:
        _remove_officer_from_naughty_list(full_name)

    success, error_message = _save_officer_github_membership(officer_obj, officer_position,
                                                             github_api=github_api,
                                                             github_teams=github_teams)
    if not success:
        officer_obj.delete()
        return success, error_message
    subject = "Welcome to the CSSS"
    body = None
    if send_email_notification:
        logger.info(
            "[about/officer_management_helper.py save_officer_and_grant_digital_resources()] "
            f"sending email notification to user {officer_obj} who is in the officer position {officer_position}"
        )
        if officer_position not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
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
        elif officer_position in ELECTION_OFFICER_POSITIONS:
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
                return False, ("Could not find any credentials for the gmail sfucsss@gmail.com account "
                               "in order to send notification email")
            sfu_csss_credentials = gmail_credentials[0]
            success, error_message = _send_instructional_email_to_new_officer(
                subject,
                body,
                "SFU CSSS",
                sfu_csss_credentials.username,
                full_name,
                f"{sfuid}@sfu.ca",
                sfu_csss_credentials.password
            )
            if not success:
                officer_obj.delete()
            return success, error_message
    return True, None


def _get_term_season_number(term):
    """
    Gets the term number using the term object

    Keyword Arguments
    term -- the term object that the function will return its number

    Returns
    term_season_number -- the number of the tem, e.g. 1, 2, or 3. this can also be -1 if the
        term does not have a valid season
    """
    if term.term == FIRST_TERM_SEASON:
        return 1
    elif term.term == SECOND_TERM_SEASON:
        return 2
    elif term.term == THIRD_TERM_SEASON:
        return 3
    return -1


def _save_officer_github_membership(officer, position, github_api=None, github_teams=None):
    """
    Adds the officers to the necessary github teams.
    they will get added both to the default GITHUB_OFFICER_TEAM
    as well as any other position specific github teams. If however, github_teams is specified, they will only
    get added to the teams specified in that array

    Keyword Arguments
    officer -- the officer to add to the github teams
    position -- the position of the officer
    github_api -- the github object that is used to communicate with github API
    github_teams -- the specific teams that the officer should be added to. This has higher
     priority than any other designation
    if specified

    return
    success -- true or false Bool
    error_message -- the error_message if success is False or None otherwise
    """
    if github_teams is None:
        logger.info(
            "[about/officer_management_helper.py _save_officer_github_membership()] "
            "github_teams is None, will save the officer under regular designations"
        )
        if position not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
            if github_api is not None:
                success, error_message = github_api.add_non_officer_to_a_team(
                    [officer.github_username],
                    GITHUB_OFFICER_TEAM
                )
                if not success:
                    logger.info(
                        "[about/officer_management_helper.py _save_officer_github_membership()] "
                        f"unable to add officer {officer.github_username} to team {GITHUB_OFFICER_TEAM} due to error "
                        f"{error_message}"
                    )
                    return False, error_message
            OfficerGithubTeam(team_name=GITHUB_OFFICER_TEAM, officer=officer).save()
            logger.info(
                "[about/officer_management_helper.py _save_officer_github_membership()] "
                f"mapped officer {officer} to team {GITHUB_OFFICER_TEAM}"
            )
        applicable_github_teams = OfficerGithubTeamMapping.objects.filter(position=position)
        for github_team in applicable_github_teams:
            if github_api is not None:
                success, error_message = github_api.add_non_officer_to_a_team(
                    [officer.github_username],
                    github_team.team_name
                )
                if not success:
                    logger.info(
                        "[about/officer_management_helper.py _save_officer_github_membership()] "
                        f"unable to add officer {officer.github_username} to team {GITHUB_OFFICER_TEAM} due to error "
                        f"{error_message}"
                    )
                    return False, error_message
            OfficerGithubTeam(team_name=github_team, officer=officer).save()
            logger.info(
                "[about/officer_management_helper.py _save_officer_github_membership()] "
                f"mapped officer {officer} to team {github_team}"
            )
    else:
        logger.info(
            "[about/officer_management_helper.py _save_officer_github_membership()] "
            f"github_teams is set to {github_teams}, will save the officer under those teams"
        )
        for team in github_teams:
            if github_api is not None:
                success, error_message = github_api.add_non_officer_to_a_team(
                    [officer.github_username],
                    team
                )
                if not success:
                    logger.info(
                        "[about/officer_management_helper.py _save_officer_github_membership()] "
                        f"unable to add officer {officer.github_username} to team {GITHUB_OFFICER_TEAM} due to error "
                        f"{error_message}"
                    )
                    return False, error_message
            OfficerGithubTeam(team_name=team, officer=officer).save()
            logger.info(
                "[about/officer_management_helper.py _save_officer_github_membership()] "
                f"mapped officer {officer} to team {team}"
            )
    return True, None


def _remove_officer_from_naughty_list(full_name):
    """
    Removes the office form the naughty list so that their permissions remain
    even after a validation

    Keyword Argument
    full_name -- the full name of the officer
    """
    naughty_officers = NaughtyOfficer.objects.all()
    for naughty_officer in naughty_officers:
        if naughty_officer.name in full_name:
            naughty_officer.delete()
            return


def _send_instructional_email_to_new_officer(subject, body, from_name, from_email, to_name, to_email, password):
    """
    Sends instruction email to the new officer on what resources are what and where to look for documentation

    subject -- the subject of the email
    body -- the body of the email
    from_name -- the name to use in the from section of email
    from_email -- the email to send the email from
    to_name -- the name of the person to send the email to
    to_email -- the email address to send the email to
    password -- the password for the from_email

    Return
    success - true or False
    error_message -- error message if success if False
    """
    logger.info("[about/officer_management_helper.py _send_instructional_email_to_new_officer()] setting up "
                "MIMEMultipart object")
    msg = MIMEMultipart()
    msg['From'] = from_name + " <" + from_email + ">"
    msg['To'] = to_name + " <" + to_email + ">"
    msg['Subject'] = subject
    msg.attach(MIMEText(body))
    logger.info("[about/officer_management_helper.py _send_instructional_email_to_new_officer()] Connecting to "
                "smtp.gmail.com:587")
    success = False
    max_number_of_retries = 5
    number_of_retries = 0
    while not success:
        try:
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.connect("smtp.gmail.com:587")
            server.ehlo()
            server.starttls()
            logger.info(
                f"[about/officer_management_helper.py _send_instructional_email_to_new_officer()] "
                f"Logging into your {from_email}"
            )
            server.login(from_email, password)
            logger.info(
                "[about/officer_management_helper.py _send_instructional_email_to_new_officer()] Sending email...")
            server.send_message(from_addr=from_email, to_addrs=to_email, msg=msg)
            success = True
            server.close()
        except Exception as e:
            number_of_retries += 1
            if number_of_retries == max_number_of_retries:
                return False, f"Experienced Error {e}"
            success = False
    logger.info("[about/officer_management_helper.py _send_instructional_email_to_new_officer()] email sent")
    return True, None
