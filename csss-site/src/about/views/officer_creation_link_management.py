import csv
import datetime
import logging
import random
import string
from io import StringIO

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from about.models import OfficerEmailListAndPositionMapping, Term, Officer, AnnouncementEmailAddress
from about.views.officer_management_helper import get_term_number, save_new_term, \
    save_officer_and_grant_digital_resources, TAB_STRING, HTML_VALUE_ATTRIBUTE_FOR_DATE, \
    ELECTION_OFFICER_POSITIONS, OFFICER_WITH_NO_ACCESS_TO_CSSS_DIGITAL_RESOURCES, \
    OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE, HTML_VALUE_ATTRIBUTE_FOR_OVERWRITING_OFFICERS, \
    HTML_VALUE_ATTRIBUTE_FOR_START_DATE, TERM_SEASONS
from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY, create_main_context, \
    ERROR_MESSAGES_KEY
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
HTML_SFUID_KEY = 'sfuid'
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


def verify_passphrase_access_and_create_context(request, tab):
    """
    Verifies that the user is allowed to access the request page depending on their passphrase

    Keyword Arguments
    request -- the django request object
    tab -- the indicator of what section the html page belongs to

    Returns
    render redirect -- the page to direct to if an error is encountered with the passphrase
    context -- the context that gets returned if no error is detected
    error_message -- the error message to display on the error page
    new_officer_details -- the details for the officer who needs to be saved
    """
    if HTML_PASSPHRASE_GET_KEY in request.GET or HTML_PASSPHRASE_POST_KEY in request.POST \
            or HTML_PASSPHRASE_SESSION_KEY in request.session:
        new_officer_details = None
        if HTML_PASSPHRASE_GET_KEY in request.GET:
            new_officer_details = request.GET[HTML_PASSPHRASE_GET_KEY]
        elif HTML_PASSPHRASE_POST_KEY in request.POST:
            new_officer_details = request.POST[HTML_PASSPHRASE_POST_KEY]
        elif HTML_PASSPHRASE_SESSION_KEY in request.session:
            new_officer_details = request.session[HTML_PASSPHRASE_SESSION_KEY]
            del request.session[HTML_PASSPHRASE_SESSION_KEY]

        new_officer_details = ProcessNewOfficer.objects.all().filter(passphrase=new_officer_details)
        logger.info(
            "[about/officer_creation_link_management.py verify_passphrase_access_and_create_context()] "
            f"len(passphrase) = '{len(new_officer_details)}'"
        )
        if len(new_officer_details) == 0:
            error_message = "You did not supply a passphrase that matched any in the records"
            return HttpResponseRedirect(f'{settings.URL_ROOT}error'), None, error_message, None
        logger.info(
            f"[about/officer_creation_link_management.py verify_passphrase_access_and_create_context()]"
            f" passphrase[0].used = '{new_officer_details[0].used}'")
        if new_officer_details[0].used:
            error_message = "the passphrase supplied has already been used"
            return HttpResponseRedirect(f'{settings.URL_ROOT}error'), None, error_message, None
    else:
        return HttpResponseRedirect(f'{settings.URL_ROOT}error'), None, "You did not supply a passphrase", None
    groups = list(request.user.groups.values_list('name', flat=True))
    context = create_main_context(request, tab, groups)
    return None, context, None, new_officer_details[0]


def show_create_link_page(request):
    """
    Shows the page where the user can select the year, term and positions for who, to create the generation links
    """
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = f'{error_message}<br>'
        return render_value
    logger.info(f"[about/officer_creation_link_management.py verify_passphrase_access_and_create_context()] "
                f"request.POST={request.POST}")
    context.update(create_term_context_variable())
    context['positions'] = "\n".join(
        [position.officer_position
         for position in OfficerEmailListAndPositionMapping.objects.all().filter(
            marked_for_deletion=False).order_by(
            'position_index')
         ]
    )
    return render(request, 'about/process_new_officer/show_create_link_for_officer_page.html', context)


def show_page_with_creation_links(request):
    """
    Will generate passphrase objects for the positions the user specified and display them
    """
    logger.info(
        f"[about/officer_creation_link_management.py show_page_with_creation_links()] request.POST={request.POST}")
    logger.info(
        f"[about/officer_creation_link_management.py show_page_with_creation_links()] request.GET={request.GET}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = f'{error_message}<br>'
        return render_value
    post_keys = [HTML_TERM_KEY, HTML_YEAR_KEY, HTML_POSITION_KEY, HTML_OVERWRITE_KEY, HTML_NEW_START_DATE_KEY,
                 HTML_DATE_KEY]
    if len(set(post_keys).intersection(request.POST.keys())) != len(post_keys):
        error_messages = "Invalid number of POST keys detected"
        logger.info(f"[about/officer_creation_link_management.py show_page_with_creation_links()] {error_messages}")
        return redirect_user_to_create_link_page(request, context, [error_messages])

    if not f"{request.POST[HTML_YEAR_KEY]}".isdigit():
        error_messages = "Specified year is not a number"
        logger.info(f"[about/officer_creation_link_management.py show_page_with_creation_links()] {error_messages}")
        return redirect_user_to_create_link_page(request, context, [error_messages])

    # ensuring that all the necessary keys are in the POST call
    logger.info("[about/officer_creation_link_management.py show_page_with_creation_links()] correct numbers of "
                "request.POST keys detected")
    year = int(request.POST[HTML_YEAR_KEY])
    # this is necessary if the user is testing the site locally and therefore is using the port to access the
    # browser
    if settings.PORT is None:
        base_url = f"{settings.HOST_ADDRESS}{settings.URL_ROOT}about/allow_officer_to_choose_name?"
    else:
        base_url = f"{settings.HOST_ADDRESS}:{settings.PORT}{settings.URL_ROOT}" \
                   "about/allow_officer_to_choose_name?"
    user_specified_positions = request.POST[HTML_POSITION_KEY].splitlines()
    if request.POST[HTML_OVERWRITE_KEY] == "true":
        delete_current_term(year, request.POST[HTML_TERM_KEY])
    new_officers_to_process = []
    error_messages = []
    validation_for_user_inputted_positions_is_successful = True
    for position in user_specified_positions:
        success, officer_details, error_message = get_next_position_number_for_term(position)
        if not success:
            validation_for_user_inputted_positions_is_successful = False
            error_messages.append(error_message)
            logger.info(
                "[about/officer_creation_link_management.py show_page_with_creation_links()] "
                f"encountered error {error_messages} when processing position {position}"
            )
        else:
            # creating the necessary passphrases and officer info for the user inputted position
            passphrase = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
            new_officers_to_process.append(
                ProcessNewOfficer(
                    passphrase=passphrase,
                    term=request.POST[HTML_TERM_KEY],
                    year=year,
                    position_name=position,
                    position_index=officer_details.position_index,
                    sfu_officer_mailing_list_email=officer_details.email,
                    link=f"{base_url}{HTML_PASSPHRASE_GET_KEY}={passphrase}",
                    new_start_date=request.POST[HTML_NEW_START_DATE_KEY] == "true",
                    start_date=datetime.datetime.strptime(
                        f"{request.POST[HTML_DATE_KEY]}",
                        '%Y-%m-%d')
                )
            )
            logger.info(
                "[about/officer_creation_link_management.py show_page_with_creation_links()] "
                f"processed position {position}"
            )
    if validation_for_user_inputted_positions_is_successful:
        logger.info("[about/officer_creation_link_management.py show_page_with_creation_links()] all requested"
                    " position were determined to be valid")
        officer_creation_links = []
        for new_officer_to_process in new_officers_to_process:
            new_officer_to_process.save()
            officer_creation_links.append(
                (new_officer_to_process.position_name, new_officer_to_process.link.replace(" ", "%20"))
            )
        context[HTML_OFFICER_CREATION_LINKS_KEY] = officer_creation_links
        return render(request, 'about/process_new_officer/show_generated_officer_links.html', context)
    else:
        logger.info("[about/officer_creation_link_management.py show_page_with_creation_links()] at least one "
                    "of the requested position were determined to be not valid")
        return redirect_user_to_create_link_page(request, context, error_messages)



def redirect_user_to_create_link_page(request, context, error_messages):
    """
    directs the user back to the page where they get asked what officers need to be created for the specified term

    Keyword Argument
    request -- the django request object
    context -- the context to pass to the html
    error_messages -- a list of all pertinent error messages
    user_specific_position -- if specified, takes in a list of officer position specified by the user

    Return
    render -- redirects user to create links page
    """
    context.update(create_term_context_variable())
    if HTML_TERM_KEY in request.POST:
        context['current_term'] = request.POST[HTML_TERM_KEY]
    if HTML_YEAR_KEY in request.POST:
        context['current_year'] = int(request.POST[HTML_YEAR_KEY])
    if HTML_POSITION_KEY in request.POST:
        context['positions'] = "\n".join(request.POST[HTML_POSITION_KEY].splitlines())
    if HTML_DATE_KEY in request.POST:
        context[HTML_VALUE_ATTRIBUTE_FOR_DATE] = request.POST[HTML_DATE_KEY]
    if HTML_OVERWRITE_KEY in request.POST:
        context[HTML_VALUE_ATTRIBUTE_FOR_OVERWRITING_OFFICERS] = request.POST[HTML_OVERWRITE_KEY]
    if HTML_NEW_START_DATE_KEY in request.POST:
        context[HTML_VALUE_ATTRIBUTE_FOR_START_DATE] = request.POST[HTML_NEW_START_DATE_KEY]
    context[ERROR_MESSAGES_KEY] = error_messages
    return render(request, 'about/process_new_officer/show_create_link_for_officer_page.html', context)


def delete_current_term(year, term):
    """
    Deletes the officers under the specified term

    Keyword Argument
    year -- the year for the term to delete
    term_season -- the season that the term takes place in, e.g. Spring, Summer or Fall
    """
    term_number = get_term_number(year, term)
    term_obj = Term.objects.all().filter(term=term, term_number=term_number, year=year)
    logger.info(f"[about/officer_creation_link_management.py delete_current_term()] deleting all officers under term"
                f"{year} {term}, for which there are {len(term_obj)} existent term[S] ")
    if len(term_obj) > 0:
        term_obj = term_obj[0]
        officer_in_selected_term = Officer.objects.all().filter(elected_term=term_obj)
        for officer in officer_in_selected_term:
            officer.delete()
    new_officer_details = ProcessNewOfficer.objects.all().filter(term=term, year=year)
    for new_officer in new_officer_details:
        new_officer.delete()


def get_next_position_number_for_term(officer_position):
    """
    Get the next term position number that is available for a term with the specified officer_position

    Keyword Arguments
    officer_position -- the position of the officer that needs to be added to the term

    Return
    success - True or False
    position_mapping -- the information to assign to user
    error_message -- error message if position does not exist
    """
    position_mapping = OfficerEmailListAndPositionMapping.objects.all().filter(position_name=officer_position,
                                                                               marked_for_deletion=False)
    if len(position_mapping) == 0:
        return False, None, f"position '{officer_position} is not valid"
    return True, position_mapping[0], None


def allow_officer_to_choose_name(request):
    """
    either shows the users a page that lets them copy a past bio to re-use if one of those past bios
    belong to them or just automatically redirects them to the page that asks them for their info

    """
    logger.info(
        f"[about/officer_creation_link_management.py allow_officer_to_choose_name()] request.POST={request.POST}")
    (render_value, context, error_message, new_officer_details) = \
        verify_passphrase_access_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = f'{error_message}<br>'
        return render_value
    officers = Officer.objects.all().filter().order_by('-elected_term__term_number', 'position_index',
                                                       '-start_date')

    request.session[HTML_REQUEST_SESSION_PASSPHRASE_KEY] = f"{new_officer_details.passphrase}"

    # if there are no past officer, the user just get sent directly to the page that asks for their info
    # otherwise, it will first ask them if one of the previous bios is theirs and they want to re-use it
    if len(officers) == 0:
        return HttpResponseRedirect(f'{settings.URL_ROOT}about/display_page_for_officer_to_input_info')

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
    (render_value, context, error_message, new_officer_details) = \
        verify_passphrase_access_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = f'{error_message}<br>'
        return render_value

    # relevant if there was an issue with processing the user input. they get redirected to this page and get shown
    # the error message along with the info they had originally entered
    if ERROR_MESSAGE_KEY in request.session:
        return \
            display_page_for_officers_to_input_their_info_alongside_error_experienced(request,
                                                                                      new_officer_details.passphrase,
                                                                                      context)
    else:
        if 'reuse_bio' in request.POST:
            officer = Officer.objects.get(id=request.POST['past_officer_bio_selected'])
        else:
            # this also covers "create_new_bio" in request.POST.keys() and when there was a re-direct
            # on the previous page because no past officer exists
            officer = None
        request.session[HTML_REQUEST_SESSION_PASSPHRASE_KEY] = new_officer_details.passphrase
        context[HTML_VALUE_ATTRIBUTE_FOR_TERM] = new_officer_details.term
        context[HTML_VALUE_ATTRIBUTE_FOR_YEAR] = new_officer_details.year
        context[HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION] = new_officer_details.position_name
        context[HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION_NUMBER] = new_officer_details.position_index
        context[HTML_VALUE_ATTRIBUTE_FOR_OFFICER_EMAIL_CONTACT] = new_officer_details.sfu_officer_mailing_list_email
        context[HTML_VALUE_ATTRIBUTE_FOR_DATE] = \
            determine_new_start_date_for_officer(
                new_officer_details.start_date, officer, new_officer_details.new_start_date
            )
        context[HTML_VALUE_ATTRIBUTE_FOR_NAME] = "" if officer is None else officer.name
        context[HTML_VALUE_ATTRIBUTE_FOR_SFUID] = "" if officer is None else officer.sfuid
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
    context[ERROR_MESSAGE_KEY] = request.session[ERROR_MESSAGE_KEY]
    del request.session[ERROR_MESSAGE_KEY]
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


def determine_new_start_date_for_officer(start_date, previous_officer, new_start_date=True):
    """
    determine whether or not the officer's start date should be in the current term or previous term

    Keyword Argument
    start_date -- the new start-date
    previous_officer -- the previous officer's info that the user wants to reuse, or a None
     object if the user did not select one
    new_start_date -- indicates whether or not the officer's start-date should use a previous date

    Return
    start_date -- the start date that needs to be used as indicated by "new_start_date"
    """
    if new_start_date or previous_officer is None or previous_officer.start_date is None:
        return start_date.strftime("%A, %d %b %Y %I:%m %S %p")
    else:
        return previous_officer.start_date.strftime("%A, %d %b %Y %I:%m %S %p")


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
    (render_value, context, error_message, new_officer_details) = \
        verify_passphrase_access_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = f'{error_message}<br>'
        return render_value

    if HTML_TERM_POSITION_KEY not in request.POST:
        return redirect_back_to_input_page_with_error_message(
            request,
            new_officer_details.passphrase,
            "the position was not detected in your submission"
        )

    officer_position = request.POST[HTML_TERM_POSITION_KEY]

    # these are the keys that are relevant to OFFICER_WITH_NO_GITHUB_ACCESS
    # it does not get its own if statement cause all of these keys are also relevant to the other officers
    post_keys = [
        HTML_TERM_KEY, HTML_YEAR_KEY, HTML_TERM_POSITION_KEY, HTML_TERM_POSITION_NUMBER_KEY,
        HTML_NAME_KEY, HTML_DATE_KEY, HTML_SFUID_KEY, HTML_EMAIL_KEY, HTML_PHONE_NUMBER_KEY,
        HTML_COURSE1_KEY, HTML_COURSE2_KEY, HTML_LANGUAGE1_KEY, HTML_LANGUAGE2_KEY, HTML_BIO_KEY,
        HTML_OFFICER_EMAIL_CONTACT_KEY
    ]
    if officer_position in ELECTION_OFFICER_POSITIONS:
        post_keys.extend([HTML_GITHUB_USERNAME_KEY])
    elif officer_position not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
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
        sfuid = request.POST[HTML_SFUID_KEY].strip()
        sfu_email_alias = request.POST[HTML_SFUID_EMAIL_ALIAS_KEY].strip()
        start_date = request.POST[HTML_DATE_KEY].strip()
        github_username = request.POST[HTML_GITHUB_USERNAME_KEY].strip() \
            if officer_position not in OFFICER_WITH_NO_ACCESS_TO_CSSS_DIGITAL_RESOURCES else ""

        gmail = request.POST[HTML_GMAIL_KEY].strip() \
            if officer_position not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE else ""
        course1 = request.POST[HTML_COURSE1_KEY].strip()
        course2 = request.POST[HTML_COURSE2_KEY].strip()
        language1 = request.POST[HTML_LANGUAGE1_KEY].strip()
        language2 = request.POST[HTML_LANGUAGE2_KEY].strip()
        bio = request.POST[HTML_BIO_KEY].strip()
        sfu_officer_mailing_list_email = request.POST[HTML_OFFICER_EMAIL_CONTACT_KEY].strip()
        post_dict = parser.parse(request.POST.urlencode())
        announcement_email = [
            email.strip()
            for row in csv.reader(StringIO(post_dict[HTML_EMAIL_KEY]), delimiter=',')
            for email in row
        ]
        success = False
        if officer_position not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
            gdrive = GoogleDrive(settings.GDRIVE_TOKEN_LOCATION, settings.GDRIVE_ROOT_FOLDER_ID)
            if gdrive.connection_successful is False:
                logger.info("[about/officer_creation_link_management.py process_information_entered_by_officer()]"
                            f" {gdrive.error_message}")
                return redirect_back_to_input_page_with_error_message(
                    request,
                    new_officer_details.passphrase,
                    gdrive.error_message
                )
            github = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
            if github.connection_successful is False:
                logger.info("[about/officer_creation_link_management.py process_information_entered_by_officer()]"
                            f" {github.error_message}")
                return redirect_back_to_input_page_with_error_message(
                    request,
                    new_officer_details.passphrase,
                    github.error_message
                )
            gitlab = GitLabAPI(settings.GITLAB_PRIVATE_TOKEN)
            if gitlab.connection_successful is False:
                logger.info("[about/officer_creation_link_management.py process_information_entered_by_officer()]"
                            f" {gitlab.error_message}")
                return redirect_back_to_input_page_with_error_message(
                    request,
                    new_officer_details.passphrase,
                    gitlab.error_message
                )
            success, error_message = save_officer_and_grant_digital_resources(
                phone_number,
                officer_position, full_name,
                sfuid, sfu_email_alias,
                announcement_email,
                github_username, gmail,
                start_date, course1, course2,
                language1, language2, bio,
                position_index, term_obj,
                sfu_officer_mailing_list_email,
                remove_from_naughty_list=True,
                github_api=github,
                gdrive_api=gdrive,
                gitlab_api=gitlab,
                send_email_notification=True
            )
        elif officer_position in ELECTION_OFFICER_POSITIONS:
            github = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
            if github.connection_successful is False:
                error_message = "unable to authenticate against CSSS Github"
                logger.info("[about/officer_creation_link_management.py process_information_entered_by_officer()]"
                            f" {error_message}")
                return redirect_back_to_input_page_with_error_message(
                    request,
                    new_officer_details.passphrase,
                    error_message
                )
            success, error_message = save_officer_and_grant_digital_resources(
                phone_number,
                officer_position, full_name,
                sfuid, sfu_email_alias,
                announcement_email,
                github_username, gmail,
                start_date, course1, course2,
                language1, language2, bio,
                position_index, term_obj,
                sfu_officer_mailing_list_email,
                remove_from_naughty_list=True,
                github_api=github,
                send_email_notification=True
            )
        elif officer_position in OFFICER_WITH_NO_ACCESS_TO_CSSS_DIGITAL_RESOURCES:
            success, error_message = save_officer_and_grant_digital_resources(
                phone_number,
                officer_position, full_name,
                sfuid, sfu_email_alias,
                announcement_email,
                github_username, gmail,
                start_date, course1, course2,
                language1, language2, bio,
                position_index, term_obj,
                sfu_officer_mailing_list_email,
                send_email_notification=True
            )
        if success is False:
            logger.info("[about/officer_creation_link_management.py process_information_entered_by_officer()]"
                        f" unable to save the officer due to {error_message}")
            return redirect_back_to_input_page_with_error_message(
                request,
                new_officer_details.passphrase,
                error_message
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
            error_message
        )


def redirect_back_to_input_page_with_error_message(request, passphrase, error_message):
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
    request.session[ERROR_MESSAGE_KEY] = error_message
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


def create_term_context_variable():
    """
    create the context dictionary for the page where the user can generate officer creation links

    return
    the context dictionary
    """
    context = {
        'terms': TERM_SEASONS,
        'years': [year for year in reversed(list(range(1970, datetime.datetime.now().year + 1)))]
    }
    current_date = datetime.datetime.now()
    if int(current_date.month) <= 4:
        context['current_term'] = context['terms'][0]
    elif int(current_date.month) <= 8:
        context['current_term'] = context['terms'][1]
    else:
        context['current_term'] = context['terms'][2]
    context['current_year'] = current_date.year
    current_date = datetime.datetime.now()
    context[HTML_VALUE_ATTRIBUTE_FOR_DATE] = current_date.strftime("%Y-%m-%d")
    context[HTML_VALUE_ATTRIBUTE_FOR_TIME] = current_date.strftime("%H:%M")
    return context
