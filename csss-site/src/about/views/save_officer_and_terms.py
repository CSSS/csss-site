import datetime
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings

from about.models import Term, Officer, AnnouncementEmailAddress
from resource_management.models import GoogleMailAccountCredentials, OfficerGithubTeam, OfficerGithubTeamMapping, \
    NaughtyOfficer

ELECTION_OFFICER_POSITIONS = [
    "By-Election Officer", "General Election Officer",
]

OFFICER_WITH_NO_GITHUB_ACCESS = [
    "SFSS Council-Representative"
]
TERM_SEASONS = ['Spring', 'Summer', "Fall"]
OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE = []
OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE.extend(OFFICER_WITH_NO_GITHUB_ACCESS)
OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE.extend(ELECTION_OFFICER_POSITIONS)

GITHUB_OFFICER_TEAM = "officers"

logger = logging.getLogger('csss_site')


def get_term_number(year, term_season):
    """gets the term number using the year and term

    Keyword Arguments
    year -- the current year in YYYY format
    term_season -- the season that the term takes place in, e.g. Spring, Summer or Fall

    returns the term_number, which is in the format YYYY<1/2/3>

    """
    term_number = int(year) * 10
    if term_season == "Spring":
        return term_number + 1
    elif term_season == "Summer":
        return term_number + 2
    elif term_season == "Fall":
        return term_number + 3


def save_new_term(year, term):
    term_number = get_term_number(year, term)
    term_obj, created = Term.objects.get_or_create(
        term=term,
        term_number=term_number,
        year=int(year)
    )
    return term_obj


def get_term_info(term):
    """gets the term year, term number and term identifier using the term object

    Keyword Arguments
    term -- the term object that the function will return its year, number and identifier for

    Returns
    term_year -- the year for the term object
    term_season_number -- the number of the tem, e.g. 1, 2, or 3. this can also be -1 if the
        term does not have a valid season
    term_season -- the season for the term, e.g. Spring, Summer or Fall
    """
    term_year = term.year
    term_season = term.term
    if term_season == "Spring":
        term_season_number = 1
    elif term_season == "Summer":
        term_season_number = 2
    elif term_season == "Fall":
        term_season_number = 3
    else:
        term_season_number = -1
    return term_year, term_season_number, term_season


def create_new_term(year, term):
    term_number = get_term_number(year, term)
    term_obj = Term.objects.all().filter(term=term, term_number=term_number, year=int(year))
    if len(term_obj) == 0:
        term_obj = Term(term=term, term_number=term_number, year=int(year))
        term_obj.save()
    else:
        term_obj = term_obj[0]
        officers = Officer.objects.all().filter(elected_term=term_obj)
        for officer in officers:
            officer.delete()
    return term_obj


def save_officer_and_grant_digital_resources(term_obj, phone_number, officer_position, full_name, full_name_in_pic,
                                             sfuid, announcement_emails, github_username, gmail, start_date,
                                             fav_course_1, fav_course_2, fav_language_1, fav_language_2, bio,
                                             position_index, grant_digital_resources=True, github=None, gdrive=None,
                                             gitlab=None):
    (term_year, term_season_number, term_identifier) = get_term_info(term_obj)
    if settings.OFFICER_PHOTOS_PATH is None:
        pic_path = (
            f"OFFICER_PHOTOS_PATH/{term_year}_0{term_season_number}_"
            f"{term_identifier}/{full_name_in_pic}.jpg"
        )
    else:
        pic_path = (
            f"{settings.OFFICER_PHOTOS_PATH}/{term_year}_0"
            f"{term_season_number}_{term_identifier}/{full_name_in_pic}.jpg"
        )
    officer_obj = Officer()
    officer_obj.position = officer_position
    officer_obj.term_position_number = position_index
    officer_obj.name = full_name
    officer_obj.sfuid = sfuid
    officer_obj.phone_number = phone_number
    officer_obj.github_username = github_username
    officer_obj.gmail = gmail
    officer_obj.course1 = fav_course_1
    officer_obj.course2 = fav_course_2
    officer_obj.language1 = fav_language_1
    officer_obj.language2 = fav_language_2
    officer_obj.bio = bio
    officer_obj.image = pic_path
    officer_obj.elected_term = term_obj
    if type(start_date) == datetime.datetime:
        # if taking in the start_date time an imported json or csv
        officer_obj.start_date = start_date
    else:
        # if taking in the start_date from the form that the new officers have to fill in
        officer_obj.start_date = datetime.datetime.strptime(start_date, "%A, %d %b %Y %I:%m %S %p")
    officer_obj.save()
    logger.info(
        "[administration/manage_officers.py process_information_entered_by_officer()] "
        f"saved user term={term_obj} full_name={full_name} officer_position={officer_position}"
    )

    for email in announcement_emails:
        save_email_to_database(email, officer_obj)
    if grant_digital_resources:
        save_officer_github_membership(github, officer_obj, officer_position)
        if officer_position not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
            gdrive.add_users_gdrive([gmail])
            gitlab.add_officer_to_csss_group([sfuid])
    remove_officer_from_naughty_list(full_name)
    subject = "Welcome to the CSSS"
    body = None
    if grant_digital_resources:
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
            sfu_csss_credentials = GoogleMailAccountCredentials.objects.all().filter(username="sfucsss@gmail.com")[0]
            send_instructional_email_to_new_officer(
                subject,
                body,
                "SFU CSSS",
                sfu_csss_credentials.username,
                full_name,
                f"{sfuid}@sfu.ca",
                sfu_csss_credentials.password
            )
    return officer_obj


def save_email_to_database(email, officer_object):
    """Saves the email that the officer may use for the announcements

    Keyword Arguments
    email -- the email the officer may use
    officer_object -- the officer who may use the email

    """
    AnnouncementEmailAddress(
        email=email,
        officer=officer_object
    ).save()


def save_officer_github_membership(github, officer, position):
    """Adds the officers to the necessary github teams.
    they will get added both to the default GITHUB_OFFICER_TEAM
    as well as any other position specific github teams

    Keyword Arguments
    officer -- the officer to add to the github teams
    position -- the position of the officer
    """
    if position not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
        github.add_non_officer_to_a_team([officer.github_username], GITHUB_OFFICER_TEAM)
        OfficerGithubTeam(team_name=GITHUB_OFFICER_TEAM, officer=officer).save()
    applicable_github_teams = OfficerGithubTeamMapping.objects.filter(position=position)
    for github_team in applicable_github_teams:
        github.add_non_officer_to_a_team([officer.github_username], github_team.team_name)
        OfficerGithubTeam(team_name=github_team, officer=officer).save()


def remove_officer_from_naughty_list(full_name):
    """Removes the office form the naughty list so that their permissions remain
    even after a validation

    Keyword Argument
    full_name -- the full name of the officer
    """
    naughty_officers = NaughtyOfficer.objects.all()
    for naughty_officer in naughty_officers:
        if naughty_officer.name in full_name:
            naughty_officer.delete()
            return


def send_instructional_email_to_new_officer(subject, body, from_name, from_email, to_name, to_email, password):
    """Sends instruction email to the new officer on what resources are what and where to look for documentation

    subject -- the subject of the email
    body -- the body of the email
    from_name -- the name to use in the from section of email
    from_email -- the email to send the email from
    to_name -- the name of the person to send the email to
    to_email -- the email address to send the email to
    password -- the password for the from_email
    """
    logger.info("[administration/manage_officers.py send_instructional_email_to_new_officer()] setting up "
                "MIMEMultipart object")
    msg = MIMEMultipart()
    msg['From'] = from_name + " <" + from_email + ">"
    msg['To'] = to_name + " <" + to_email + ">"
    msg['Subject'] = subject
    msg.attach(MIMEText(body))
    logger.info("[administration/manage_officers.py send_instructional_email_to_new_officer()] Connecting to "
                "smtp.gmail.com:587")
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.connect("smtp.gmail.com:587")
    server.ehlo()
    server.starttls()
    logger.info(
        f"[administration/manage_officers.py send_instructional_email_to_new_officer()] "
        f"Logging into your {from_email}"
    )
    server.login(from_email, password)
    logger.info("[administration/manage_officers.py send_instructional_email_to_new_officer()] Sending email...")
    server.send_message(from_addr=from_email, to_addrs=to_email, msg=msg)
    server.close()
