import csv
import datetime
import logging
from io import StringIO

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from about.models import Officer, AnnouncementEmailAddress
from about.views.officer_position_and_github_mapping.officer_management_helper import save_new_term, \
    save_officer_and_grant_digital_resources, TAB_STRING, HTML_VALUE_ATTRIBUTE_FOR_DATE, \
    ELECTION_OFFICER_POSITIONS, OFFICER_WITH_NO_ACCESS_TO_CSSS_DIGITAL_RESOURCES, \
    OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE, TERM_SEASONS
from csss.views.context_creation.create_main_context import create_main_context
from csss.views.views import ERROR_MESSAGES_KEY
from csss.views_helper import get_current_term_number, SUMMER_TERM_NUMBER, FALL_TERM_NUMBER, SPRING_TERM_NUMBER, \
    get_last_summer_term, get_last_fall_term, get_last_spring_term
from resource_management.models import ProcessNewOfficer
from resource_management.views.resource_apis.gdrive.gdrive_api import GoogleDrive
from resource_management.views.resource_apis.github.github_api import GitHubAPI
from resource_management.views.resource_apis.gitlab.gitlab_api import GitLabAPI

logger = logging.getLogger('csss_site')

# used on show_create_link_for_officer_page
HTML_TERM_KEY = 'term'
HTML_YEAR_KEY = 'year'
HTML_DATE_KEY = 'date'
HTML_POSITION_KEY = 'positions'
HTML_OVERWRITE_KEY = 'overwrite'
HTML_NEW_START_DATE_KEY = 'new_start_date'

# the key used to indicate passphrase in link given to the new officers
HTML_PASSPHRASE_GET_KEY = HTML_PASSPHRASE_POST_KEY = HTML_REQUEST_SESSION_PASSPHRASE_KEY = \
    HTML_PASSPHRASE_SESSION_KEY = 'passphrase'

# used on show_generated_officer_links
HTML_OFFICER_CREATION_LINKS_KEY = 'officer_creation_links'

# used on add_officer page
HTML_VALUE_ATTRIBUTE_FOR_TERM = 'term_value'
HTML_VALUE_ATTRIBUTE_FOR_YEAR = 'year_value'
HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION = 'term_position_value'
HTML_TERM_POSITION_KEY = 'term_position'
HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION_NUMBER = 'term_position_number_value'
HTML_TERM_POSITION_NUMBER_KEY = 'position_index'
HTML_VALUE_ATTRIBUTE_FOR_OFFICER_EMAIL_CONTACT = 'sfu_email_list_address_value'
HTML_OFFICER_EMAIL_CONTACT_KEY = 'sfu_email_list_address'
HTML_VALUE_ATTRIBUTE_FOR_NAME = 'name_value'
HTML_NAME_KEY = 'name'
HTML_VALUE_ATTRIBUTE_FOR_SFUID = 'sfuid_value'
HTML_SFUID_KEY = 'sfu_computing_id'
HTML_VALUE_ATTRIBUTE_FOR_SFUID_EMAIL_ALIAS = 'sfuid_email_alias_value'
HTML_SFUID_EMAIL_ALIAS_KEY = 'sfuid_email_alias'
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

# used on allow_officer_to_choose_name page
HTML_PAST_OFFICERS_KEY = 'past_officers'

HTML_VALUE_ATTRIBUTE_FOR_TIME = "time_value"

PASSPHRASE_ERROR_KEY = 'passphrase_error'
REQUEST_SESSION_USER_INPUT_ERROR_KEY = 'user_input_error'

YEAR_LONG_OFFICER_POSITIONS_START_IN_SPRING = ["Frosh Week Chair"]
YEAR_LONG_OFFICER_POSITION_START_IN_SUMMER = [
    "President", "Vice-President", "Treasurer", "Director of Resources", "Director of Events",
    "Assistant Director of Events", "Director of Communications", "Director of Archives",
    "SFSS Council Representative"
]
TWO_TERM_POSITIONS_START_IN_FALL = [
    "First Year Representative 1", "First Year Representative 2"
]


def verify_passphrase_access_and_create_context(request, tab):
    """
    Verifies that the user is allowed to access the request page depending on their passphrase

    Keyword Arguments
    request -- the django request object
    tab -- the indicator of what section the html page belongs to

    Returns
    success -- True or False
    context -- the context that gets returned if no error is detected
    new_officer_details -- the details for the officer who needs to be saved
    passphrase -- the passphrase entered by the user
    """
    context = create_main_context(request, tab=tab)
    passphrase = request.GET.get(HTML_PASSPHRASE_GET_KEY, None)
    if passphrase is None:
        passphrase = request.POST.get(HTML_PASSPHRASE_POST_KEY, None)
    if passphrase is None:
        passphrase = request.session.get(HTML_PASSPHRASE_SESSION_KEY, None)
        if passphrase is not None:
            del request.session[HTML_PASSPHRASE_SESSION_KEY]
    if passphrase is None:
        context[PASSPHRASE_ERROR_KEY] = "You did not supply a passphrase"
        return False, context, None, None
    context['HTML_PASSPHRASE_GET_KEY'] = HTML_PASSPHRASE_GET_KEY
    context[HTML_PASSPHRASE_GET_KEY] = passphrase

    new_officer_details = ProcessNewOfficer.objects.all().filter(passphrase=passphrase)
    logger.info(
        "[about/officer_creation_link_management.py verify_passphrase_access_and_create_context()] "
        f"len(passphrase) = '{len(new_officer_details)}'"
    )
    if len(new_officer_details) != 1:
        context[PASSPHRASE_ERROR_KEY] = "Passphrase is not attached to a record for a new Officer"
        return False, context, None, passphrase
    new_officer_detail = new_officer_details[0]
    logger.info(
        f"[about/officer_creation_link_management.py verify_passphrase_access_and_create_context()]"
        f" new_officer_detail.used = '{new_officer_detail.used}'")
    if new_officer_detail.used:
        context[PASSPHRASE_ERROR_KEY] = "the passphrase supplied has already been used"
        return False, context, None, passphrase
    return True, context, new_officer_detail, passphrase

def allow_officer_to_choose_name(request):
    """
    either shows the users a page that lets them copy a past bio to re-use if one of those past bios
    belong to them or just automatically redirects them to the page that asks them for their info

    """
    logger.info(
        f"[about/officer_creation_link_management.py allow_officer_to_choose_name()] request.POST={request.POST}")

    (successful, context, new_officer_details, passphrase) = verify_passphrase_access_and_create_context(
        request, TAB_STRING
    )

    error_message = request.session.get(PASSPHRASE_ERROR_KEY, None)
    if error_message is not None:
        # if passphrase validation did not work when trying to render page where user inputs their data
        # or when trying to parse the passphrase when processing the user's input
        del request.session[PASSPHRASE_ERROR_KEY]
        context[ERROR_MESSAGES_KEY] = [error_message]
        return render(request, 'about/process_new_officer/allow_officer_to_choose_name.html', context)
    if not successful:
        # if user used the wrong passphrase to either select a previous officer bio or use a new bio
        context[ERROR_MESSAGES_KEY] = [context[PASSPHRASE_ERROR_KEY]]
        return render(request, 'about/process_new_officer/allow_officer_to_choose_name.html', context)
    officers = Officer.objects.all().filter().order_by('-elected_term__term_number', 'position_index',
                                                       '-start_date')
    # if there are no past officer, the user just get sent directly to the page that asks for their info
    # otherwise, it will first ask them if one of the previous bios is theirs and they want to re-use it
    if len(officers) == 0:
        return HttpResponseRedirect(
            f'{settings.URL_ROOT}about/display_page_for_officer_to_input_info?{HTML_PASSPHRASE_GET_KEY}=' + passphrase
        )

    context[HTML_PAST_OFFICERS_KEY] = officers
    return render(request, 'about/process_new_officer/allow_officer_to_choose_name.html', context)


def display_page_for_officers_to_input_their_info(request):
    """
    Shows the page where a user is asked to input their info. this page will also pre-populated the necessary fields
    if the user indicated on the previous page that they want to re-use one of their past bios

    """
    logger.info(
        "[about/officer_creation_link_management.py display_page_for_officers_to_input_their_info()] "
        f"request.GET={request.GET}"
    )
    (successful, context, new_officer_details, passphrase) = verify_passphrase_access_and_create_context(
        request, TAB_STRING
    )
    if not successful:
        request.session[PASSPHRASE_ERROR_KEY] = context[PASSPHRASE_ERROR_KEY]
        return HttpResponseRedirect(
            f"{settings.URL_ROOT}about/allow_officer_to_choose_name?{HTML_PASSPHRASE_GET_KEY}={passphrase}"
        )

    # relevant if there was an issue with processing the user input. they get redirected back to
    # this page and get shown the error message along with the info they had originally entered
    if REQUEST_SESSION_USER_INPUT_ERROR_KEY in request.session:
        return \
            display_page_for_officers_to_input_their_info_alongside_error_experienced(request,
                                                                                      new_officer_details.passphrase,
                                                                                      context)
    else:
        officer = None
        reuse_bio_selected = 'reuse_bio' in request.POST
        past_bio_selected = 'past_officer_bio_selected' in request.POST
        bio_selected_id_is_digit = False
        if past_bio_selected:
            bio_selected_id_is_digit = f"{request.POST['past_officer_bio_selected']}".isdigit()
        bio_selected_id_is_valid = False
        if bio_selected_id_is_digit:
            bio_selected_id_is_valid = (
                    len(Officer.objects.all().filter(id=int(request.POST['past_officer_bio_selected']))) == 1
            )
        if reuse_bio_selected and bio_selected_id_is_valid:
            officer = Officer.objects.get(id=int(request.POST['past_officer_bio_selected']))
        request.session[HTML_REQUEST_SESSION_PASSPHRASE_KEY] = new_officer_details.passphrase
        context[HTML_VALUE_ATTRIBUTE_FOR_TERM] = new_officer_details.term
        context[HTML_VALUE_ATTRIBUTE_FOR_YEAR] = new_officer_details.year
        context[HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION] = new_officer_details.position_name
        context[HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION_NUMBER] = new_officer_details.position_index
        context[HTML_VALUE_ATTRIBUTE_FOR_OFFICER_EMAIL_CONTACT] = new_officer_details.sfu_officer_mailing_list_email
        context[HTML_VALUE_ATTRIBUTE_FOR_DATE] = determine_new_start_date_for_officer(
            new_officer_details, officer
        )
        context[HTML_VALUE_ATTRIBUTE_FOR_NAME] = "" if officer is None else officer.full_name
        context[HTML_VALUE_ATTRIBUTE_FOR_SFUID] = "" if officer is None else officer.sfu_computing_id
        context[HTML_VALUE_ATTRIBUTE_FOR_SFUID_EMAIL_ALIAS] = "" if officer is None else officer.sfu_email_alias
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

        logger.info(f"[about/officer_creation_link_management.py "
                    f"display_page_for_officers_to_input_their_info()] context set to '{context}'")
        logger.info(
            "[about/officer_creation_link_management.py display_page_for_officers_to_input_their_info()] returning "
            "'about/process_new_officer/add_officer.html'")
        return render(request, 'about/process_new_officer/add_officer.html', context)


def display_page_for_officers_to_input_their_info_alongside_error_experienced(request, passphrase, context):
    """
    Displays the input page for the user along with the information they had already inputted and the error message

    Keyword Argument
    request --- the django request object
    passphrase -- the passphrase for the link
    context -- context for the html render

    Return
    render -- the render object that directs the user back to the page for inputting info
    """
    context[ERROR_MESSAGES_KEY] = request.session[REQUEST_SESSION_USER_INPUT_ERROR_KEY].split("<br>")

    del request.session[REQUEST_SESSION_USER_INPUT_ERROR_KEY]
    request.session[HTML_REQUEST_SESSION_PASSPHRASE_KEY] = passphrase
    context[HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION] = request.session[HTML_TERM_POSITION_KEY]
    del request.session[HTML_TERM_POSITION_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_TERM] = request.session[HTML_TERM_KEY]
    del request.session[HTML_TERM_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_YEAR] = request.session[HTML_YEAR_KEY]
    del request.session[HTML_YEAR_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_PHONE_NUMBER] = request.session[HTML_PHONE_NUMBER_KEY]
    del request.session[HTML_PHONE_NUMBER_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION_NUMBER] = request.session[HTML_TERM_POSITION_NUMBER_KEY]
    del request.session[HTML_TERM_POSITION_NUMBER_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_NAME] = request.session[HTML_NAME_KEY]
    del request.session[HTML_NAME_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_SFUID] = request.session[HTML_SFUID_KEY]
    del request.session[HTML_SFUID_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_SFUID_EMAIL_ALIAS] = request.session[HTML_SFUID_EMAIL_ALIAS_KEY]
    del request.session[HTML_SFUID_EMAIL_ALIAS_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_DATE] = request.session[HTML_DATE_KEY]
    del request.session[HTML_DATE_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_GITHUB_USERNAME] = request.session[HTML_GITHUB_USERNAME_KEY]
    del request.session[HTML_GITHUB_USERNAME_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_GMAIL] = request.session[HTML_GMAIL_KEY]
    del request.session[HTML_GMAIL_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_COURSE1] = request.session[HTML_COURSE1_KEY]
    del request.session[HTML_COURSE1_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_COURSE2] = request.session[HTML_COURSE2_KEY]
    del request.session[HTML_COURSE2_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_LANGUAGE1] = request.session[HTML_LANGUAGE1_KEY]
    del request.session[HTML_LANGUAGE1_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_LANGUAGE2] = request.session[HTML_LANGUAGE2_KEY]
    del request.session[HTML_LANGUAGE2_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_BIO] = request.session[HTML_BIO_KEY]
    del request.session[HTML_BIO_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_OFFICER_EMAIL_CONTACT] = request.session[HTML_OFFICER_EMAIL_CONTACT_KEY]
    del request.session[HTML_OFFICER_EMAIL_CONTACT_KEY]
    context[HTML_VALUE_ATTRIBUTE_FOR_EMAIL] = request.session[HTML_EMAIL_KEY]
    del request.session[HTML_EMAIL_KEY]
    logger.info(
        "[about/officer_creation_link_management.py "
        "display_page_for_officers_to_input_their_info_alongside_error_experienced()] context set to "
        f"{context}")
    return render(request, 'about/process_new_officer/add_officer.html', context)


def determine_new_start_date_for_officer(process_new_officer, officer):
    """
    determine whether or not the officer's start date should be in the current term or previous term

    Keyword Argument
    process_new_officer -- the details for the officer who needs to be saved
    officer -- the bio for the officer whose bio is being re-used

    Return
    start_date -- the start date that needs to be used as indicated by "use_new_start_date"
    """
    logger.info(
        "[about/officer_creation_link_management.py "
        "determine_new_start_date_for_officer()] process_new_officer.use_new_start_date="
        f"{process_new_officer.use_new_start_date}"
    )

    if process_new_officer.use_new_start_date or officer is None:
        return process_new_officer.start_date.strftime("%A, %d %b %Y %I:%m %S %p")

    officer_name = officer.full_name
    position_name = process_new_officer.position_name
    current_term_number = get_current_term_number()
    logger.info(
        "[about/officer_creation_link_management.py "
        "determine_new_start_date_for_officer()] name of officer to find start date for ="
        f"{officer.full_name}"
    )
    logger.info(
        "[about/officer_creation_link_management.py "
        "determine_new_start_date_for_officer()] position_name to find start_date for ="
        f"{position_name}"
    )
    logger.info(
        "[about/officer_creation_link_management.py "
        "determine_new_start_date_for_officer()] current_term_number ="
        f"{current_term_number}"
    )
    past_bios_for_officer = None
    if (
            position_name in YEAR_LONG_OFFICER_POSITIONS_START_IN_SPRING and
            current_term_number in [SUMMER_TERM_NUMBER, FALL_TERM_NUMBER]):
        start_date_for_last_spring_term = get_last_spring_term()
        logger.info(
            "[about/officer_creation_link_management.py "
            "determine_new_start_date_for_officer()] start_date_for_last_spring_term="
            f"{start_date_for_last_spring_term}"
        )
        past_bios_for_officer = Officer.objects.all().order_by('-start_date').filter(
            full_name=officer_name, position_name=position_name,
            start_date__gte=start_date_for_last_spring_term
        )
    elif (
            position_name in YEAR_LONG_OFFICER_POSITION_START_IN_SUMMER and
            current_term_number in [FALL_TERM_NUMBER, SPRING_TERM_NUMBER]):
        start_date_for_last_summer_term = get_last_summer_term()
        logger.info(
            "[about/officer_creation_link_management.py "
            "determine_new_start_date_for_officer()] start_date_for_last_summer_term="
            f"{start_date_for_last_summer_term}"
        )
        past_bios_for_officer = Officer.objects.all().order_by('-start_date').filter(
            full_name=officer_name, position_name=position_name,
            start_date__gte=start_date_for_last_summer_term
        )
    elif (
            position_name in TWO_TERM_POSITIONS_START_IN_FALL
            and current_term_number == SPRING_TERM_NUMBER):
        start_date_for_last_fall_term = get_last_fall_term()
        logger.info(
            "[about/officer_creation_link_management.py "
            "determine_new_start_date_for_officer()] start_date_for_last_fall_term="
            f"{start_date_for_last_fall_term}"
        )
        past_bios_for_officer = Officer.objects.all().order_by('-start_date').filter(
            full_name=officer_name, position_name=position_name,
            start_date__gte=get_last_fall_term()
        )
    if past_bios_for_officer is None:
        logger.info(
            "[about/officer_creation_link_management.py determine_new_start_date_for_officer()] "
            "No queries were performed, will use a new start date"
        )
        return process_new_officer.start_date.strftime("%A, %d %b %Y %I:%m %S %p")
    logger.info(
        "[about/officer_creation_link_management.py determine_new_start_date_for_officer()] "
        f"{len(past_bios_for_officer)} past bios for officer found with the specified constraints"
    )
    if len(past_bios_for_officer) == 0:
        logger.info(
            "[about/officer_creation_link_management.py determine_new_start_date_for_officer()] "
            "using new start date since no past bios for officer found with the specified constraints"
        )
        return process_new_officer.start_date.strftime("%A, %d %b %Y %I:%m %S %p")
    past_bio_for_officer = past_bios_for_officer[0]
    logger.info(
        "[about/officer_creation_link_management.py determine_new_start_date_for_officer()] "
        "using the start date attached to officer"
        f"{past_bio_for_officer.position_name} for term {past_bio_for_officer.elected_term} which is "
        f"{past_bio_for_officer.start_date.strftime('%A, %d %b %Y %I:%m %S %p')}"
    )
    return past_bio_for_officer.start_date.strftime("%A, %d %b %Y %I:%m %S %p")


def validate_sfuid_and_github(gitlab_api=None, sfu_computing_id=None, github_username=None):
    """
    Verify that the given sfu_computing_id has access to gitlab, the given github_username exists and
     is in the SFU CSSS Github org

    Keyword Argument
    gitlab -- the gitlab api
    sfu_computing_id -- the sfu_computing_id to validate
    github_username -- the github username to validate

    Return
    error_message -- a list of possible error messages to display for the officer
    """
    error_messages = []
    if gitlab_api is not None:
        if sfu_computing_id is None:
            error_messages.append("No SFU ID is provided")
            logger.info(
                f"[about/officer_creation_link_management.py validate_sfuid_and_github()] {error_messages}"
            )
        else:
            success, error_message = gitlab_api.validate_username(sfu_computing_id)
            if not success:
                error_messages.append(error_message)
    if github_username is not None:
        github_api = GitHubAPI()
        success, error_message = github_api.validate_user(github_username)
        if not success:
            error_messages.append(error_message)
        else:
            success, error_message = github_api.verify_user_in_org(github_username, invite_user=True)
            if not success:
                error_messages.append(error_message)
    return error_messages


def process_information_entered_by_officer(request):
    """
    1. Takes in the information entered by the officer and creates a new officer object based on it.
    2. gives them access to the SFU CSSS Github org on Github, the SFU CSSS Google Drive and also the SFU CSSS org
    on SFU Gitlab depending on if their position requires that level of access
    3. sends them an email at their sfu email with the necessary instructions and documentation on being an officer
    and using our digital resources

    """
    logger.info(
        f"[about/officer_creation_link_management.py "
        f"process_information_entered_by_officer()] request.POST={request.POST}")
    (successful, context, new_officer_details, passphrase) = verify_passphrase_access_and_create_context(request,
                                                                                                         TAB_STRING)
    if not successful:
        request.session[PASSPHRASE_ERROR_KEY] = context[PASSPHRASE_ERROR_KEY]
        return HttpResponseRedirect(
            f"{settings.URL_ROOT}about/allow_officer_to_choose_name?{HTML_PASSPHRASE_GET_KEY}={passphrase}"
        )

    if HTML_TERM_POSITION_KEY not in request.POST:
        return redirect_back_to_input_page_with_error_message(
            request,
            new_officer_details.passphrase,
            error_message="the position was not detected in your submission"
        )

    position_name = request.POST[HTML_TERM_POSITION_KEY]

    # these are the keys that are relevant to OFFICER_WITH_NO_GITHUB_ACCESS
    # it does not get its own if statement cause all of these keys are also relevant to the other officers
    post_keys = [
        HTML_TERM_KEY, HTML_YEAR_KEY, HTML_TERM_POSITION_KEY, HTML_TERM_POSITION_NUMBER_KEY,
        HTML_NAME_KEY, HTML_DATE_KEY, HTML_SFUID_KEY, HTML_EMAIL_KEY, HTML_PHONE_NUMBER_KEY,
        HTML_COURSE1_KEY, HTML_COURSE2_KEY, HTML_LANGUAGE1_KEY, HTML_LANGUAGE2_KEY, HTML_BIO_KEY,
        HTML_OFFICER_EMAIL_CONTACT_KEY
    ]
    if position_name in ELECTION_OFFICER_POSITIONS:
        post_keys.extend([HTML_GITHUB_USERNAME_KEY])
    elif position_name not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
        post_keys.extend([HTML_GITHUB_USERNAME_KEY, HTML_GMAIL_KEY])

    if len(set(request.POST.keys()).intersection(post_keys)) == len(post_keys):
        logger.info("[about/officer_creation_link_management.py process_information_entered_by_officer()]"
                    " correct number of request.POST keys detected")
        term_obj = save_new_term(request.POST[HTML_YEAR_KEY], request.POST[HTML_TERM_KEY])
        phone_number = 0 if request.POST[HTML_PHONE_NUMBER_KEY] == '' else int(request.POST[HTML_PHONE_NUMBER_KEY])
        position_index = \
            0 if request.POST[HTML_TERM_POSITION_NUMBER_KEY] == '' \
            else int(request.POST[HTML_TERM_POSITION_NUMBER_KEY])
        full_name = request.POST[HTML_NAME_KEY].strip()
        sfu_computing_id = request.POST[HTML_SFUID_KEY].strip()
        sfu_email_alias = request.POST[HTML_SFUID_EMAIL_ALIAS_KEY].strip()
        start_date = request.POST[HTML_DATE_KEY].strip()
        github_username = request.POST[HTML_GITHUB_USERNAME_KEY].strip() \
            if position_name not in OFFICER_WITH_NO_ACCESS_TO_CSSS_DIGITAL_RESOURCES else ""

        gmail = request.POST[HTML_GMAIL_KEY].strip() \
            if position_name not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE else ""
        course1 = request.POST[HTML_COURSE1_KEY].strip()
        course2 = request.POST[HTML_COURSE2_KEY].strip()
        language1 = request.POST[HTML_LANGUAGE1_KEY].strip()
        language2 = request.POST[HTML_LANGUAGE2_KEY].strip()
        bio = request.POST[HTML_BIO_KEY].strip()
        sfu_officer_mailing_list_email = request.POST[HTML_OFFICER_EMAIL_CONTACT_KEY].strip()
        post_dict = parser.parse(request.POST.urlencode())
        announcement_email = [
            email.strip().lower()
            for row in csv.reader(StringIO(post_dict[HTML_EMAIL_KEY]), delimiter=',')
            for email in row
        ]
        success = False
        if position_name not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
            gdrive = GoogleDrive()
            if gdrive.connection_successful is False:
                logger.info("[about/officer_creation_link_management.py process_information_entered_by_officer()]"
                            f" {gdrive.error_message}")
                return redirect_back_to_input_page_with_error_message(
                    request,
                    new_officer_details.passphrase,
                    error_message=gdrive.error_message
                )
            gitlab_api = GitLabAPI(settings.GITLAB_PRIVATE_TOKEN)
            if gitlab_api.connection_successful is False:
                logger.info("[about/officer_creation_link_management.py process_information_entered_by_officer()]"
                            f" {gitlab_api.error_message}")
                return redirect_back_to_input_page_with_error_message(
                    request,
                    new_officer_details.passphrase,
                    error_message=gitlab_api.error_message
                )
            error_messages = validate_sfuid_and_github(gitlab_api=gitlab_api, sfu_computing_id=sfu_computing_id,
                                                       github_username=github_username)
            if len(error_messages) > 0:
                return redirect_back_to_input_page_with_error_message(
                    request,
                    new_officer_details.passphrase,
                    error_messages=error_messages
                )
            success, error_message = save_officer_and_grant_digital_resources(
                phone_number,
                full_name,
                sfu_computing_id, sfu_email_alias,
                announcement_email,
                github_username, gmail,
                start_date, course1, course2,
                language1, language2, bio,
                position_name, position_index, term_obj,
                sfu_officer_mailing_list_email,
                remove_from_naughty_list=True,
                gdrive_api=gdrive,
                gitlab_api=gitlab_api,
                send_email_notification=True
            )
        elif position_name in ELECTION_OFFICER_POSITIONS:
            error_messages = validate_sfuid_and_github(github_username=github_username)
            if len(error_messages) > 0:
                return redirect_back_to_input_page_with_error_message(
                    request,
                    new_officer_details.passphrase,
                    error_messages=error_messages
                )
            success, error_message = save_officer_and_grant_digital_resources(
                phone_number,
                full_name,
                sfu_computing_id, sfu_email_alias,
                announcement_email,
                github_username, gmail,
                start_date, course1, course2,
                language1, language2, bio,
                position_name, position_index, term_obj,
                sfu_officer_mailing_list_email,
                remove_from_naughty_list=True,
                send_email_notification=True
            )
        elif position_name in OFFICER_WITH_NO_ACCESS_TO_CSSS_DIGITAL_RESOURCES:
            success, error_message = save_officer_and_grant_digital_resources(
                phone_number,
                full_name,
                sfu_computing_id, sfu_email_alias,
                announcement_email,
                github_username, gmail,
                start_date, course1, course2,
                language1, language2, bio,
                position_name, position_index, term_obj,
                sfu_officer_mailing_list_email,
                send_email_notification=True
            )
        if success is False:
            logger.info("[about/officer_creation_link_management.py process_information_entered_by_officer()]"
                        f" unable to save the officer due to {error_message}")
            return redirect_back_to_input_page_with_error_message(
                request,
                new_officer_details.passphrase,
                error_message=error_message
            )
        logger.info("[about/officer_creation_link_management.py process_information_entered_by_officer()]"
                    " successfully saved the officer and set their digital resources")
        new_officer_details.used = True
        new_officer_details.save()
        return render(request, 'about/process_new_officer/success.html', context)
    else:
        error_message = "Invalid number of POST keys detected"
        logger.info("[about/officer_creation_link_management.py process_information_entered_by_officer()]"
                    f" unable to save the officer due to {error_message}")
        return redirect_back_to_input_page_with_error_message(
            request,
            new_officer_details.passphrase,
            error_message=error_message
        )


def redirect_back_to_input_page_with_error_message(request, passphrase, error_message=None, error_messages=None):
    """
    populates the request.session with the necessary fields for the user and redirects the user back to the page
    where they need to be displayed along with the relevant error message

    Keyword Argument
    request --- the django request object
    passphrase -- the passphrase for the link
    error_message -- the error experienced when processing the user inputs

    Return
    render -- the render object that directs the user back to the page for inputting info
    """
    if error_message is not None and type(error_message) is str:
        request.session[REQUEST_SESSION_USER_INPUT_ERROR_KEY] = error_message
    elif error_messages is not None and type(error_messages) is list:
        request.session[REQUEST_SESSION_USER_INPUT_ERROR_KEY] = "<br>".join(error_messages)
    request.session[HTML_REQUEST_SESSION_PASSPHRASE_KEY] = passphrase
    request.session[HTML_TERM_POSITION_KEY] = request.POST[HTML_TERM_POSITION_KEY]
    request.session[HTML_TERM_KEY] = request.POST[HTML_TERM_KEY]
    request.session[HTML_YEAR_KEY] = request.POST[HTML_YEAR_KEY]
    request.session[HTML_PHONE_NUMBER_KEY] = request.POST[HTML_PHONE_NUMBER_KEY]
    request.session[HTML_TERM_POSITION_NUMBER_KEY] = request.POST[HTML_TERM_POSITION_NUMBER_KEY]
    request.session[HTML_NAME_KEY] = request.POST[HTML_NAME_KEY]
    request.session[HTML_SFUID_KEY] = request.POST[HTML_SFUID_KEY]
    request.session[HTML_SFUID_EMAIL_ALIAS_KEY] = request.POST[HTML_SFUID_EMAIL_ALIAS_KEY]
    request.session[HTML_DATE_KEY] = request.POST[HTML_DATE_KEY]
    request.session[HTML_GITHUB_USERNAME_KEY] = request.POST[HTML_GITHUB_USERNAME_KEY]
    request.session[HTML_GMAIL_KEY] = request.POST[HTML_GMAIL_KEY]
    request.session[HTML_COURSE1_KEY] = request.POST[HTML_COURSE1_KEY]
    request.session[HTML_COURSE2_KEY] = request.POST[HTML_COURSE2_KEY]
    request.session[HTML_LANGUAGE1_KEY] = request.POST[HTML_LANGUAGE1_KEY]
    request.session[HTML_LANGUAGE2_KEY] = request.POST[HTML_LANGUAGE2_KEY]
    request.session[HTML_BIO_KEY] = request.POST[HTML_BIO_KEY]
    request.session[HTML_OFFICER_EMAIL_CONTACT_KEY] = request.POST[HTML_OFFICER_EMAIL_CONTACT_KEY]
    request.session[HTML_EMAIL_KEY] = request.POST[HTML_EMAIL_KEY]
    return HttpResponseRedirect(f"{settings.URL_ROOT}about/display_page_for_officer_to_input_info")