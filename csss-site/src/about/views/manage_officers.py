import csv
import datetime
import logging
import random
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import StringIO

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from about.models import Term, Officer, AnnouncementEmailAddress
from resource_management.models import ProcessNewOfficer, NaughtyOfficer, \
    OfficerGithubTeamMapping, OfficerGithubTeam, GoogleMailAccountCredentials
from resource_management.views.resource_apis.gdrive.gdrive_api import GoogleDrive
from resource_management.views.resource_apis.github.github_api import GitHubAPI
from resource_management.views.resource_apis.gitlab.gitlab_api import GitLabAPI
from csss.views_helper import verify_access_logged_user_and_create_context, create_main_context, ERROR_MESSAGE_KEY

# used on show_create_link_for_officer_page
HTML_TERM_KEY = 'term'
HTML_YEAR_KEY = 'year'
HTML_POSITION_KEY = 'positions'
HTML_OVERWRITE_KEY = 'overwrite'

# the key used to indicate passphrase in link given to the new officers
HTML_PASSPHRASE_GET_KEY = 'passphrase'
HTML_PASSPHRASE_POST_KEY = 'passphrase'
HTML_PASSPHRASE_SESSION_KEY = 'passphrase'

HTML_REQUEST_SESSION_PASSPHRASE_KEY = 'passphrase'

# used on show_generated_officer_links
HTML_OFFICER_CREATION_LINKS_KEY = 'officer_creation_links'

# used on allow_officer_to_choose_name page
HTML_PAST_OFFICERS_KEY = 'past_officers'

# used on add_officer page
HTML_VALUE_ATTRIBUTE_FOR_TERM = 'term_value'
HTML_TERM_KEY
HTML_VALUE_ATTRIBUTE_FOR_YEAR = 'year_value'
HTML_YEAR_KEY
HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION = 'term_position_value'
HTML_TERM_POSITION_KEY = 'term_position'
HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION_NUMBER = 'term_position_number_value'
HTML_TERM_POSITION_NUMBER_KEY = 'term_position_number'
HTML_VALUE_ATTRIBUTE_FOR_NAME = 'name_value'
HTML_NAME_KEY = 'name'
HTML_VALUE_ATTRIBUTE_FOR_SFUID = 'sfuid_value'
HTML_SFUID_KEY = 'sfuid'
HTML_VALUE_ATTRIBUTE_FOR_EMAIL = 'email_value'
HTML_EMAIL_KEY = 'email'
HTML_VALUE_ATTRIBUTE_FOR_GMAIL = 'gmail_value'
HTML_GMAIL_KEY = 'gmail'
HTML_VALUE_ATTRIBUTE_FOR_PHONE_NUMBER = 'phone_number_value'
HTML_PHONE_NUMBER_KEY = 'phone_number'
HTML_VALUE_ATTRIBUTE_FOR_GITHUB_USERNAME = 'github_username_value'
HTML_GITHUB_USERNAME_KEY = 'github_username'
HTML_VALUE_ATTRIBUTE_FOR_COURSE1 = 'course1_value'
HTML_COURSE1_KEY = 'course1'
HTML_VALUE_ATTRIBUTE_FOR_COURSE2 = 'course2_value'
HTML_COURSE2_KEY = 'course2'
HTML_VALUE_ATTRIBUTE_FOR_LANGUAGE1 = 'language1_value'
HTML_LANGUAGE1_KEY = 'language1'
HTML_VALUE_ATTRIBUTE_FOR_LANGUAGE2 = 'language2_value'
HTML_LANGUAGE2_KEY = 'language2'
HTML_VALUE_ATTRIBUTE_FOR_BIO = 'bio_value'
HTML_BIO_KEY = 'bio'

GITHUB_OFFICER_TEAM = "officers"

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
TAB_STRING = 'about'

logger = logging.getLogger('csss_site')


def verify_passphrase_access_and_create_context(request, tab):
    """Verifies that the user is allowed to access the request page depending on their passphrase

    Keyword Arguments

    request -- the django request object
    tab -- the indicator of what section the html page belongs to

    Returns

    render redirect -- the page to direct to if an error is encountered with the passphrase
    context -- the context that gets returned if no error is detected
    error_message -- the error message to display on the error page
    passphrase -- the db object that is retrieved using the passphrase the user had in their url
    """
    if HTML_PASSPHRASE_GET_KEY in request.GET or HTML_PASSPHRASE_POST_KEY in request.POST \
            or HTML_PASSPHRASE_SESSION_KEY in request.session:
        if HTML_PASSPHRASE_GET_KEY in request.GET:
            passphrase = request.GET[HTML_PASSPHRASE_GET_KEY]
        elif HTML_PASSPHRASE_POST_KEY in request.POST:
            passphrase = request.POST[HTML_PASSPHRASE_POST_KEY]
        elif HTML_PASSPHRASE_SESSION_KEY in request.session:
            passphrase = request.session[HTML_PASSPHRASE_SESSION_KEY]
            del request.session[HTML_PASSPHRASE_SESSION_KEY]

        passphrase = ProcessNewOfficer.objects.all().filter(passphrase=passphrase)
        logger.info(
            "[administration/manage_officers.py verify_passphrase_access_and_create_context()] len(passphrase) "
            f"= '{len(passphrase)}'"
        )
        if len(passphrase) == 0:
            return HttpResponseRedirect(
                '/error'), None, "You did not supply a passphrase that matched any" \
                                 " in the records", None
        logger.info(
            f"[administration/manage_officers.py verify_passphrase_access_and_create_context()] passphrase["
            f"0].used = '{passphrase[0].used}'")
        if passphrase[0].used:
            return HttpResponseRedirect(
                '/error'), None, "the passphrase supplied has already been used", None
    else:
        return HttpResponseRedirect('/error'), None, "You did not supply a passphrase", None
    groups = list(request.user.groups.values_list('name', flat=True))
    context = create_main_context(request, tab, groups)
    return None, context, None, passphrase[0]


def show_create_link_page(request):
    """Shows the page where the user can select tye year, term and positions for who, to create the
    generation links

    """
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    logger.info(f"[administration/manage_officers.py show_create_link_page()] request.POST={request.POST}")
    context['terms'] = TERM_SEASONS
    context['years'] = [year for year in list(range(1970, datetime.datetime.now().year + 1))]

    current_date = datetime.datetime.now()
    if int(current_date.month) <= 4:
        context['current_term'] = context['terms'][0]
    elif int(current_date.month) <= 8:
        context['current_term'] = context['terms'][1]
    else:
        context['current_term'] = context['terms'][2]
    return render(request, 'about/process_new_officer/show_create_link_for_officer_page.html', context)


def show_page_with_creation_links(request):
    """Will generate passphrase objects for the positions the user specified and display them

    """
    logger.info(f"[administration/manage_officers.py show_page_with_creation_links()] request.POST={request.POST}")
    logger.info(f"[administration/manage_officers.py show_page_with_creation_links()] request.GET={request.GET}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    post_keys = [HTML_TERM_KEY, HTML_YEAR_KEY, HTML_POSITION_KEY, HTML_OVERWRITE_KEY]
    if len(set(post_keys).intersection(request.POST.keys())) == len(post_keys):
        # ensuring that all the necessary keys are in the POST call
        logger.info("[administration/manage_officers.py show_page_with_creation_links()] correct numbers of "
                    "request.POST keys detected")

        # this is necessary if the user is testing the site locally and therefore is using the port to access the
        # browser
        if settings.PORT is None:
            base_url = f"{settings.HOST_ADDRESS}/about/allow_officer_to_choose_name?"
        else:
            base_url = f"{settings.HOST_ADDRESS}:{settings.PORT}/about/allow_officer_to_choose_name?"
        officer_creation_links = []
        positions = request.POST[HTML_POSITION_KEY].splitlines()
        # determines if the users that are created need to overwrite the officers for the specified term or append to
        # the list of current officers for that term
        if request.POST[HTML_OVERWRITE_KEY] == "true":
            position_number = 0
        elif request.POST[HTML_OVERWRITE_KEY] == "false":
            position_number = get_next_position_number_for_term_that_already_has_officers(request.POST[HTML_YEAR_KEY],
                                                                                          request.POST[HTML_TERM_KEY])
        for position in positions:
            # creating links for officer inputs
            passphrase = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
            link_to_create = (
                f"{base_url}{HTML_PASSPHRASE_GET_KEY}={passphrase}"
            )
            ProcessNewOfficer(
                passphrase=passphrase,
                term=request.POST[HTML_TERM_KEY],
                year=request.POST[HTML_YEAR_KEY],
                position=position,
                term_position_number=position_number,
                link=link_to_create
            ).save()
            logger.info(
                "[administration/manage_officers.py show_page_with_creation_links()] "
                f"interpreting position {position}"
            )

            link_to_create = link_to_create.replace(" ", "%20")
            officer_creation_links.append(link_to_create)
            position_number += 1
        context[HTML_OFFICER_CREATION_LINKS_KEY] = officer_creation_links
        return render(request,
                      'about/process_new_officer/show_generated_officer_links.html',
                      context)

    return HttpResponseRedirect('/')


def get_next_position_number_for_term_that_already_has_officers(year, term):
    """Get the next term position number that is available for a term

    Keyword Arguments:
        year -- the year of the tem that is being looked for
        term -- the season for the term, e.g. "Spring", "Summer", "Fall"

        If the term does not exist, 0 will be returned. Otherwise, the next available position_number
        is returned
    """
    term_number = int(year) * 10
    if term == "Spring":
        term_number = term_number + 1
    elif term == "Summer":
        term_number = term_number + 2
    elif term == "Fall":
        term_number = term_number + 3
    term_obj = Term.objects.filter(
        year=year,
        term=term,
        term_number=term_number
    )
    if len(term_obj) < 1:
        return 0
    else:
        officers = Officer.objects.all().filter(
            elected_term=term_obj[0]
        ).order_by('-term_position_number')
        logger.info(
            f"[administration/manage_officers.py get_next_position_number_for_term_that_already_has_officers()] "
            f"last officer's position number is{officers[0].term_position_number}")
        return officers[0].term_position_number + 1


def allow_officer_to_choose_name(request):
    """either shows the users a page that lets them copy a past bio to re-use if one of those past bios
    belong to them or just automatically redirects them to the page that asks them for their info

    """
    logger.info(
        f"[administration/manage_officers.py allow_officer_to_choose_name()] request.POST={request.POST}")
    (render_value, context, error_message, passphrase) = verify_passphrase_access_and_create_context(request,
                                                                                                     TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    officers = Officer.objects.all()

    # if there are no past officer, the user just get sent directly to the page that asks for their info
    # otherwise, it will first ask them if one of the previous bios is theirs and they want to re-use it
    request.session[HTML_REQUEST_SESSION_PASSPHRASE_KEY] = "{}".format(passphrase.passphrase)
    if len(officers) == 0:
        return HttpResponseRedirect('/about/display_page_for_officer_to_input_info')
    context[HTML_PAST_OFFICERS_KEY] = officers
    return render(request, 'about/process_new_officer/allow_officer_to_choose_name.html', context)


def display_page_for_officers_to_input_their_info(request):
    """Shows the page where a user is asked to input their info. this page will also pre-populated the necessary fields
    if the user indicated on the previous page that they want to re-use one of their past bios

    """
    logger.info(
        "[administration/manage_officers.py display_page_for_officers_to_input_their_info()] "
        f"request.GET={request.GET}"
    )
    (render_value, context, error_message, passphrase) = verify_passphrase_access_and_create_context(request,
                                                                                                     TAB_STRING)
    if context is None:
        request.session['error_message'] = '{}<br>'.format(error_message)
        return render_value
    if "create_new_bio" in request.POST.keys():
        officer = None
    elif 'past_officer_bio_selected' in request.POST.keys():
        officer = Officer.objects.get(id=request.POST['past_officer_bio_selected'])
    else:  # in the case where a direct re-direct was done on the previous page because no past officer exist
        officer = None
    request.session[HTML_REQUEST_SESSION_PASSPHRASE_KEY] = passphrase.passphrase
    context[HTML_VALUE_ATTRIBUTE_FOR_TERM] = passphrase.term
    context[HTML_VALUE_ATTRIBUTE_FOR_YEAR] = passphrase.year
    context[HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION] = passphrase.position
    context[HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION_NUMBER] = passphrase.term_position_number
    context[HTML_VALUE_ATTRIBUTE_FOR_NAME] = "" if officer is None else officer.name
    context[HTML_VALUE_ATTRIBUTE_FOR_SFUID] = "" if officer is None else officer.sfuid
    context[HTML_VALUE_ATTRIBUTE_FOR_EMAIL] = ", ".join(
        [email.email for email in AnnouncementEmailAddress.objects.filter(officer=officer)]
    )
    context[HTML_VALUE_ATTRIBUTE_FOR_GMAIL] = "" if officer is None else officer.gmail
    context[HTML_VALUE_ATTRIBUTE_FOR_PHONE_NUMBER] = 0 if officer is None else officer.phone_number
    context[HTML_VALUE_ATTRIBUTE_FOR_GITHUB_USERNAME] = "" if officer is None else officer.github_username
    context[HTML_VALUE_ATTRIBUTE_FOR_COURSE1] = "" if officer is None else officer.course1
    context[HTML_VALUE_ATTRIBUTE_FOR_COURSE2] = "" if officer is None else officer.course2
    context[HTML_VALUE_ATTRIBUTE_FOR_LANGUAGE1] = "" if officer is None else officer.language1
    context[HTML_VALUE_ATTRIBUTE_FOR_LANGUAGE2] = "" if officer is None else officer.language2
    context[HTML_VALUE_ATTRIBUTE_FOR_BIO] = "" if officer is None else officer.bio

    logger.info(f"[administration/manage_officers.py display_page_for_officers_to_input_their_info()] context "
                f"set to '{context}'")
    logger.info(
        "[administration/manage_officers.py display_page_for_officers_to_input_their_info()] returning "
        "'about/process_new_officer/add_officer.html'")
    return render(request, 'about/process_new_officer/add_officer.html', context)


def process_information_entered_by_officer(request):
    """
    1. Takes in the information entered by the officer and creates a new officer object based on it.
    2. gives them access to the SFU CSSS Github org on Github, the SFU CSSS Google Drive and also the SFU CSSS org
    on SFU Gitlab depending on if their position requires that level of access
    3. sends them an email at their sfu email with the necessary instructions and documentation on being an officer
    and using our digital resources

    """
    logger.info(
        f"[administration/manage_officers.py process_information_entered_by_officer()] request.POST={request.POST}")
    (render_value, context, error_message, passphrase) = verify_passphrase_access_and_create_context(request,
                                                                                                     TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value

    if HTML_TERM_POSITION_KEY not in request.POST:
        request.session[ERROR_MESSAGE_KEY] = "the position was not detected in your submission"
        return render_value

    officer_position = request.POST[HTML_TERM_POSITION_KEY]
    if officer_position in ELECTION_OFFICER_POSITIONS:
        post_keys = [
            HTML_TERM_KEY, HTML_YEAR_KEY, HTML_TERM_POSITION_KEY, HTML_TERM_POSITION_NUMBER_KEY,
            HTML_NAME_KEY, HTML_SFUID_KEY, HTML_EMAIL_KEY, HTML_PHONE_NUMBER_KEY,
            HTML_GITHUB_USERNAME_KEY, HTML_COURSE1_KEY, HTML_COURSE2_KEY, HTML_LANGUAGE1_KEY, HTML_LANGUAGE2_KEY,
            HTML_BIO_KEY
        ]
    elif officer_position in OFFICER_WITH_NO_GITHUB_ACCESS:
        post_keys = [
            HTML_TERM_KEY, HTML_YEAR_KEY, HTML_TERM_POSITION_KEY, HTML_TERM_POSITION_NUMBER_KEY,
            HTML_NAME_KEY, HTML_SFUID_KEY, HTML_EMAIL_KEY, HTML_PHONE_NUMBER_KEY,
            HTML_COURSE1_KEY, HTML_COURSE2_KEY, HTML_LANGUAGE1_KEY, HTML_LANGUAGE2_KEY,
            HTML_BIO_KEY
        ]
    elif officer_position not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
        post_keys = [
            HTML_TERM_KEY, HTML_YEAR_KEY, HTML_TERM_POSITION_KEY, HTML_TERM_POSITION_NUMBER_KEY,
            HTML_NAME_KEY, HTML_SFUID_KEY, HTML_EMAIL_KEY, HTML_GMAIL_KEY, HTML_PHONE_NUMBER_KEY,
            HTML_GITHUB_USERNAME_KEY, HTML_COURSE1_KEY, HTML_COURSE2_KEY, HTML_LANGUAGE1_KEY, HTML_LANGUAGE2_KEY,
            HTML_BIO_KEY
        ]
        gdrive = GoogleDrive(settings.GDRIVE_TOKEN_LOCATION, settings.GDRIVE_ROOT_FOLDER_ID)
        gitlab = GitLabAPI(settings.GITLAB_PRIVATE_TOKEN)

    if len(set(request.POST.keys()).intersection(post_keys)) == len(post_keys):
        logger.info("[administration/manage_officers.py process_information_entered_by_officer()] correct number of "
                    "request.POST "
                    "keys detected")
        passphrase.used = True
        passphrase.save()
        term_number = get_term_number(request.POST[HTML_YEAR_KEY], request.POST[HTML_TERM_KEY])
        term, created = Term.objects.get_or_create(
            term=request.POST[HTML_TERM_KEY],
            term_number=term_number,
            year=int(request.POST[HTML_YEAR_KEY])
        )
        phone_number = 0 if request.POST[HTML_PHONE_NUMBER_KEY] == '' else int(request.POST[HTML_PHONE_NUMBER_KEY])
        position_index = 0 if request.POST[HTML_TERM_POSITION_NUMBER_KEY] == '' else int(
            request.POST[HTML_TERM_POSITION_NUMBER_KEY])
        full_name = request.POST[HTML_NAME_KEY].strip()
        full_name_in_pic = request.POST[HTML_NAME_KEY].replace(" ", "_")
        sfuid = request.POST[HTML_SFUID_KEY].strip()
        github_username = request.POST[
            HTML_GITHUB_USERNAME_KEY].strip() if officer_position not in OFFICER_WITH_NO_GITHUB_ACCESS else ""
        gmail = request.POST[
            HTML_GMAIL_KEY].strip() if officer_position not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE else ""
        course1 = request.POST[HTML_COURSE1_KEY].strip()
        course2 = request.POST[HTML_COURSE2_KEY].strip()
        language1 = request.POST[HTML_LANGUAGE1_KEY].strip()
        language2 = request.POST[HTML_LANGUAGE2_KEY].strip()
        bio = request.POST[HTML_BIO_KEY].strip()
        (term_year, term_season_number, term_identifier) = get_term_info(term)
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

        officer, created = Officer.objects.get_or_create(
            position=officer_position,
            term_position_number=position_index,
            name=full_name,
            sfuid=sfuid,
            phone_number=phone_number,
            github_username=github_username,
            gmail=gmail,
            course1=course1,
            course2=course2,
            language1=language1,
            language2=language2,
            bio=bio,
            image=pic_path,
            elected_term=term,
        )
        logger.info(
            "[administration/manage_officers.py process_information_entered_by_officer()] "
            f"saved user term={term} full_name={full_name} officer_position={officer_position}"
        )
        post_dict = parser.parse(request.POST.urlencode())
        announcement_email = [
            email.strip()
            for row in csv.reader(StringIO(post_dict[HTML_EMAIL_KEY]), delimiter=',')
            for email in row
        ]
        for email in announcement_email:
            save_email_to_database(email, officer)
        save_officer_github_membership(officer, officer_position)
        if officer_position not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
            gdrive.add_users_gdrive([gmail])
            gitlab.add_officer_to_csss_group([sfuid])
        remove_officer_from_naughty_list(full_name)
        subject = "Welcome to the CSSS"
        body = None
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
    return HttpResponseRedirect('/')


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


def save_officer_github_membership(officer, position):
    """Adds the officers to the necessary github teams.
    they will get added both to the default GITHUB_OFFICER_TEAM
    as well as any other position specific github teams

    Keyword Arguments
    officer -- the officer to add to the github teams
    position -- the position of the officer
    """
    github = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
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
