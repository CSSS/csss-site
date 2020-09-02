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

from about.models import Term, Officer, AnnouncementEmailAddress, OfficerPositionMapping
from about.views.save_officer_and_terms import save_new_term, TERM_SEASONS, OFFICER_WITH_NO_GITHUB_ACCESS, \
    ELECTION_OFFICER_POSITIONS, OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE, save_officer_and_grant_digital_resources, \
    get_term_number
from csss.views_helper import verify_access_logged_user_and_create_context, create_main_context, ERROR_MESSAGE_KEY, \
    there_are_multiple_entries
from resource_management.models import ProcessNewOfficer
from resource_management.views.resource_apis.gdrive.gdrive_api import GoogleDrive
from resource_management.views.resource_apis.github.github_api import GitHubAPI
from resource_management.views.resource_apis.gitlab.gitlab_api import GitLabAPI

# used on show_create_link_for_officer_page
HTML_TERM_KEY = 'term'
HTML_YEAR_KEY = 'year'
HTML_DATE_KEY = 'date'
HTML_TIME_KEY = 'time'
HTML_POSITION_KEY = 'positions'
HTML_OVERWRITE_KEY = 'overwrite'
HTML_NEW_START_DATE_KEY = 'new_start_date'

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
HTML_VALUE_ATTRIBUTE_FOR_DATE = 'date_value'
HTML_DATE_KEY
HTML_VALUE_ATTRIBUTE_FOR_TIME = "time_value"
HTML_TIME_KEY
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

TAB_STRING = 'about'

logger = logging.getLogger('csss_site')

POSITION_MAPPING_INPUT_KEY = "unsuccessful_position_mappings"

OFFICER_POSITION_MAPPING_ID_KEY = "officer_position_mapping_db_id"
OFFICER_POSITION_MAPPING_POSITION_KEY = "officer_position_mapping_position"
OFFICER_POSITION_MAPPING_POSITION_INDEX_KEY = "officer_position_mapping_position_index"

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
            new_officer_details = request.GET[HTML_PASSPHRASE_GET_KEY]
        elif HTML_PASSPHRASE_POST_KEY in request.POST:
            new_officer_details = request.POST[HTML_PASSPHRASE_POST_KEY]
        elif HTML_PASSPHRASE_SESSION_KEY in request.session:
            new_officer_details = request.session[HTML_PASSPHRASE_SESSION_KEY]
            del request.session[HTML_PASSPHRASE_SESSION_KEY]

        new_officer_details = ProcessNewOfficer.objects.all().filter(passphrase=new_officer_details)
        logger.info(
            "[administration/manage_officers.py verify_passphrase_access_and_create_context()] len(passphrase) "
            f"= '{len(new_officer_details)}'"
        )
        if len(new_officer_details) == 0:
            return HttpResponseRedirect(
                '/error'), None, "You did not supply a passphrase that matched any" \
                                 " in the records", None
        logger.info(
            f"[administration/manage_officers.py verify_passphrase_access_and_create_context()] passphrase["
            f"0].used = '{new_officer_details[0].used}'")
        if new_officer_details[0].used:
            return HttpResponseRedirect(
                '/error'), None, "the passphrase supplied has already been used", None
    else:
        return HttpResponseRedirect('/error'), None, "You did not supply a passphrase", None
    groups = list(request.user.groups.values_list('name', flat=True))
    context = create_main_context(request, tab, groups)
    return None, context, None, new_officer_details[0]


def show_create_link_page(request):
    """Shows the page where the user can select tye year, term and positions for who, to create the
    generation links

    """
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    logger.info(f"[administration/manage_officers.py show_create_link_page()] request.POST={request.POST}")
    context.update(create_term_context_variable())
    context['positions'] = "\n".join([position.officer_position for position in
                                      OfficerPositionMapping.objects.all().filter(marked_for_deletion=False).order_by(
                                          'term_position_number')])
    return render(request, 'about/process_new_officer/show_create_link_for_officer_page.html', context)


def create_term_context_variable():
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


def delete_current_term(year, term):
    term_number = get_term_number(year, term)
    term_obj = Term.objects.filter(term=term, term_number=term_number, year=int(year))
    if len(term_obj) == 1:
        term_obj[0].delete()
    new_officer_details = ProcessNewOfficer.objects.filter(term=term, year=year)
    for new_officer in new_officer_details:
        new_officer.delete()


def show_page_with_creation_links(request):
    """Will generate passphrase objects for the positions the user specified and display them

    """
    logger.info(f"[administration/manage_officers.py show_page_with_creation_links()] request.POST={request.POST}")
    logger.info(f"[administration/manage_officers.py show_page_with_creation_links()] request.GET={request.GET}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    post_keys = [HTML_TERM_KEY, HTML_YEAR_KEY, HTML_POSITION_KEY, HTML_OVERWRITE_KEY, HTML_NEW_START_DATE_KEY, HTML_DATE_KEY, HTML_TIME_KEY]
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
        user_specified_positions = request.POST[HTML_POSITION_KEY].splitlines()
        if request.POST[HTML_OVERWRITE_KEY] == "true":
            delete_current_term(request.POST[HTML_YEAR_KEY], request.POST[HTML_TERM_KEY])
        new_officers_to_process = []
        error_messages = []
        validations_passed = True
        for position in user_specified_positions:
            success, position_number, error_message = get_next_position_number_for_term(position)
            if not success:
                validations_passed = False
                error_messages.append(error_message)
            else:
                # creating links for officer inputs
                passphrase = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
                new_officers_to_process.append(
                    ProcessNewOfficer(
                        passphrase=passphrase,
                        term=request.POST[HTML_TERM_KEY],
                        year=request.POST[HTML_YEAR_KEY],
                        position=position,
                        term_position_number=position_number,
                        link=f"{base_url}{HTML_PASSPHRASE_GET_KEY}={passphrase}",
                        new_start_date=request.POST[HTML_NEW_START_DATE_KEY] == "true",
                        start_date=datetime.datetime.strptime(
                            f"{request.POST[HTML_DATE_KEY]} "
                            f"{request.POST[HTML_TIME_KEY]}",
                            '%Y-%m-%d %H:%M')
                    )
                )
                logger.info(
                    "[administration/manage_officers.py show_page_with_creation_links()] "
                    f"interpreting position {position}"
                )
        if validations_passed:
            for new_officer_to_process in new_officers_to_process:
                new_officer_to_process.save()
                officer_creation_links.append((new_officer_to_process.position, new_officer_to_process.link.replace(" ", "%20")))
            context[HTML_OFFICER_CREATION_LINKS_KEY] = officer_creation_links
            return render(request, 'about/process_new_officer/show_generated_officer_links.html', context)
        else:
            context.update(create_term_context_variable())
            context['current_term'] = request.POST[HTML_TERM_KEY]
            context['current_year'] = int(request.POST[HTML_YEAR_KEY])
            context['positions'] = "\n".join(user_specified_positions)
            context['error_messages'] = error_messages
            context[HTML_VALUE_ATTRIBUTE_FOR_DATE] = request.POST[HTML_DATE_KEY]
            context[HTML_VALUE_ATTRIBUTE_FOR_TIME] = request.POST[HTML_TIME_KEY]
            return render(request, 'about/process_new_officer/show_create_link_for_officer_page.html', context)

    return HttpResponseRedirect('/')


def get_next_position_number_for_term(officer_position):
    """Get the next term position number that is available for a term with the specified officer_position

    Keyword Arguments:
        year -- the year of the tem that is being looked for
        term -- the season for the term, e.g. "Spring", "Summer", "Fall"
        officer_position -- the position of the officer that needs to be added to the term

        If the term does not exist, 0 will be returned. Otherwise, the next available position_number
        is returned or if its a position that already exists in the current term, the position number that was already
        assigned to that position number will be returned
    """
    position_mapping = OfficerPositionMapping.objects.all().filter(officer_position=officer_position,
                                                                   marked_for_deletion=False)
    if len(position_mapping) == 0:
        return False, None, f"position '{officer_position} is not valid"
    return True, position_mapping[0].term_position_number, None


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
    officers = Officer.objects.all().filter().order_by('-elected_term__term_number', 'term_position_number',
                                                       '-start_date')

    # if there are no past officer, the user just get sent directly to the page that asks for their info
    # otherwise, it will first ask them if one of the previous bios is theirs and they want to re-use it
    request.session[HTML_REQUEST_SESSION_PASSPHRASE_KEY] = "{}".format(passphrase.passphrase)
    if len(officers) == 0:
        return HttpResponseRedirect('/about/display_page_for_officer_to_input_info')
    context[HTML_PAST_OFFICERS_KEY] = officers
    return render(request, 'about/process_new_officer/allow_officer_to_choose_name.html', context)


def determine_new_start_date_for_officer(start_date, previous_start_date, new_start_date=True):
    if new_start_date or previous_start_date is None:
        return start_date.strftime("%A, %d %b %Y %I:%m %S %p")
    else:
        return previous_start_date.strftime("%A, %d %b %Y %I:%m %S %p")


def display_page_for_officers_to_input_their_info(request):
    """Shows the page where a user is asked to input their info. this page will also pre-populated the necessary fields
    if the user indicated on the previous page that they want to re-use one of their past bios

    """
    logger.info(
        "[administration/manage_officers.py display_page_for_officers_to_input_their_info()] "
        f"request.GET={request.GET}"
    )
    (render_value, context, error_message, new_officer_details) = verify_passphrase_access_and_create_context(request,
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
    request.session[HTML_REQUEST_SESSION_PASSPHRASE_KEY] = new_officer_details.passphrase
    context[HTML_VALUE_ATTRIBUTE_FOR_TERM] = new_officer_details.term
    context[HTML_VALUE_ATTRIBUTE_FOR_YEAR] = new_officer_details.year
    context[HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION] = new_officer_details.position
    context[HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION_NUMBER] = new_officer_details.term_position_number
    context[HTML_VALUE_ATTRIBUTE_FOR_DATE] = determine_new_start_date_for_officer(new_officer_details.start_date,
                                                                                  officer.start_date, new_officer_details.new_start_date)
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
            HTML_NAME_KEY, HTML_DATE_KEY, HTML_SFUID_KEY, HTML_EMAIL_KEY, HTML_PHONE_NUMBER_KEY,
            HTML_GITHUB_USERNAME_KEY, HTML_COURSE1_KEY, HTML_COURSE2_KEY, HTML_LANGUAGE1_KEY, HTML_LANGUAGE2_KEY,
            HTML_BIO_KEY
        ]
    elif officer_position in OFFICER_WITH_NO_GITHUB_ACCESS:
        post_keys = [
            HTML_TERM_KEY, HTML_YEAR_KEY, HTML_TERM_POSITION_KEY, HTML_TERM_POSITION_NUMBER_KEY,
            HTML_NAME_KEY, HTML_DATE_KEY, HTML_SFUID_KEY, HTML_EMAIL_KEY, HTML_PHONE_NUMBER_KEY,
            HTML_COURSE1_KEY, HTML_COURSE2_KEY, HTML_LANGUAGE1_KEY, HTML_LANGUAGE2_KEY,
            HTML_BIO_KEY
        ]
    elif officer_position not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
        post_keys = [
            HTML_TERM_KEY, HTML_YEAR_KEY, HTML_TERM_POSITION_KEY, HTML_TERM_POSITION_NUMBER_KEY,
            HTML_NAME_KEY, HTML_DATE_KEY, HTML_SFUID_KEY, HTML_EMAIL_KEY, HTML_GMAIL_KEY,
            HTML_PHONE_NUMBER_KEY,
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
        term_obj = save_new_term(request.POST[HTML_YEAR_KEY], request.POST[HTML_TERM_KEY])
        phone_number = 0 if request.POST[HTML_PHONE_NUMBER_KEY] == '' else int(request.POST[HTML_PHONE_NUMBER_KEY])
        position_index = 0 if request.POST[HTML_TERM_POSITION_NUMBER_KEY] == '' else int(
            request.POST[HTML_TERM_POSITION_NUMBER_KEY])
        full_name = request.POST[HTML_NAME_KEY].strip()
        full_name_in_pic = request.POST[HTML_NAME_KEY].replace(" ", "_")
        sfuid = request.POST[HTML_SFUID_KEY].strip()
        start_date = request.POST[HTML_DATE_KEY].strip()
        github_username = request.POST[
            HTML_GITHUB_USERNAME_KEY].strip() if officer_position not in OFFICER_WITH_NO_GITHUB_ACCESS else ""
        github = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
        gmail = request.POST[
            HTML_GMAIL_KEY].strip() if officer_position not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE else ""
        course1 = request.POST[HTML_COURSE1_KEY].strip()
        course2 = request.POST[HTML_COURSE2_KEY].strip()
        language1 = request.POST[HTML_LANGUAGE1_KEY].strip()
        language2 = request.POST[HTML_LANGUAGE2_KEY].strip()
        bio = request.POST[HTML_BIO_KEY].strip()
        post_dict = parser.parse(request.POST.urlencode())
        announcement_email = [
            email.strip()
            for row in csv.reader(StringIO(post_dict[HTML_EMAIL_KEY]), delimiter=',')
            for email in row
        ]
        save_officer_and_grant_digital_resources(term_obj, phone_number, officer_position, full_name, full_name_in_pic,
                                                 sfuid, announcement_email, github_username, gmail, start_date, course1,
                                                 course2, language1, language2, bio, position_index,
                                                 grant_digital_resources=True, github=github,
                                                 gdrive=gdrive, gitlab=gitlab)
    return HttpResponseRedirect('/')


def position_mapping(request):
    logger.info(
        f"[administration/manage_officers.py position_mapping()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request,
                                                                                          TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    context['OFFICER_POSITION_MAPPING_ID_KEY'] = OFFICER_POSITION_MAPPING_ID_KEY
    context['OFFICER_POSITION_MAPPING_POSITION_KEY'] = OFFICER_POSITION_MAPPING_POSITION_KEY
    context['OFFICER_POSITION_MAPPING_POSITION_INDEX_KEY'] = OFFICER_POSITION_MAPPING_POSITION_INDEX_KEY

    if request.method == "POST":
        post_dict = parser.parse(request.POST.urlencode())
        if 'action' in post_dict:
            if post_dict['action'] == "update":
                position_mapping = OfficerPositionMapping.objects.get(id=post_dict[OFFICER_POSITION_MAPPING_ID_KEY])

                new_position_index_for_officer_position = int(post_dict[OFFICER_POSITION_MAPPING_POSITION_INDEX_KEY])
                new_name_for_officer_position = post_dict[OFFICER_POSITION_MAPPING_POSITION_KEY]
                if not (
                        new_name_for_officer_position == position_mapping.officer_position and new_position_index_for_officer_position == position_mapping.term_position_number):
                    if new_name_for_officer_position == position_mapping.officer_position:
                        success, error_message = validate_position_index(new_position_index_for_officer_position)
                    else:
                        success, error_message = validate_position_mappings(new_name_for_officer_position,
                                                                            new_position_index_for_officer_position)
                    if success:
                        current_date = datetime.datetime.now()
                        term_active = (current_date.year * 10)
                        if int(current_date.month) <= 4:
                            term_active += 1
                        elif int(current_date.month) <= 8:
                            term_active += 2
                        else:
                            term_active += 3
                        term = Term.objects.get(term_number=term_active)
                        officer_in_current_term_that_need_update = Officer.objects.all().filter(elected_term=term,
                                                                                                position=position_mapping.officer_position)
                        for officer in officer_in_current_term_that_need_update:
                            officer.term_position_number = new_position_index_for_officer_position
                            officer.save()
                        position_mapping.officer_position = new_name_for_officer_position
                        position_mapping.term_position_number = new_position_index_for_officer_position
                        position_mapping.save()
                    else:
                        context[ERROR_MESSAGE_KEY] = error_message
            elif post_dict['action'] == "delete":
                position_mapping = OfficerPositionMapping.objects.get(id=post_dict[OFFICER_POSITION_MAPPING_ID_KEY])
                position_mapping.marked_for_deletion = True
                position_mapping.save()
            elif post_dict['action'] == "un_delete":
                position_mapping = OfficerPositionMapping.objects.get(id=post_dict[OFFICER_POSITION_MAPPING_ID_KEY])
                position_mapping.marked_for_deletion = False
                position_mapping.save()
        else:
            if there_are_multiple_entries(post_dict, "position"):
                number_of_entries = len(post_dict["position"])
                error_detected = False
                unsaved_position_mappings = []
                submitted_positions = []
                submitted_position_indexes = []
                for index in range(number_of_entries):
                    position_name = post_dict["position"][index]
                    position_index = post_dict["position_index"][index]
                    unsaved_position_mappings.append({
                        "Position": post_dict["position"][index],
                        "Position_Index": post_dict["position_index"][index]
                    })
                    success, error_message = validate_position_mappings(
                        position_name, position_index,
                        submitted_positions, submitted_position_indexes,
                    )
                    submitted_positions.append(position_name)
                    submitted_position_indexes.append(position_index)
                    if not success:
                        context[ERROR_MESSAGE_KEY] = error_message
                        error_detected = True
                if error_detected:
                    context["unsaved_position_mappings"] = unsaved_position_mappings
                else:
                    for index in range(number_of_entries):
                        position_name = post_dict["position"][index]
                        position_index = post_dict["position_index"][index]
                        save_position_mapping(position_name, position_index)
            else:
                success, error_message = validate_position_mappings(post_dict["position"], post_dict["position_index"])
                if success:
                    save_position_mapping(post_dict["position"], post_dict["position_index"])
                else:
                    unsaved_position_mappings = [{
                        "Position": post_dict["position"],
                        "Position_Index": post_dict["position_index"]
                    }]
                    context["unsaved_position_mappings"] = unsaved_position_mappings
                    context[ERROR_MESSAGE_KEY] = error_message
    position_mapping = OfficerPositionMapping.objects.all().order_by(
        'term_position_number')
    if len(position_mapping) > 0:
        context['position_mapping'] = position_mapping
    return render(request, 'about/officer_list_management/position_mapping.html', context)


def validate_position_index(position_index, submitted_position_indexes=[]):
    if len(OfficerPositionMapping.objects.all().filter(
            term_position_number=position_index)) > 0 or position_index in submitted_position_indexes:
        return False, f"Another Position already has an index of {position_index}"
    return True, None


def validate_position_mappings(position_name, position_index, submitted_positions=[], submitted_position_indexes=[]):
    success, error_message = validate_position_index(position_index)
    if not success:
        return success, error_message
    if len(OfficerPositionMapping.objects.all().filter(
            officer_position=position_name)) > 0 or position_name in submitted_positions:
        return False, f"the position of {position_name} already exists"
    return True, None


def save_position_mapping(position_name, position_index):
    OfficerPositionMapping(officer_position=position_name, term_position_number=position_index).save()
