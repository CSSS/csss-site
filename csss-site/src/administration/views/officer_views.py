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

from about.models import Term, Officer, AnnouncementEmailAddress, GithubTeam
from administration.models import ProcessNewOfficer, NaughtyOfficer
from .resource_apis.gdrive.gdrive_api import GoogleDrive
from .resource_apis.github.github_api import GitHubAPI
from .views_helper import verify_access_logged_user_and_create_context, verify_passphrase_access_and_create_context

INPUT_POST_KEY = 'input_json'
ANNOUNCEMENT_EMAILS_KEY = 'announcement_emails'

CONTEXT_TERM_KEY = 'term_key'
HTML_TERM_KEY = 'term'
CONTEXT_YEAR_KEY = 'year_key'
HTML_YEAR_KEY = 'year'
CONTEXT_POSITION_KEY = 'term_position_key'
HTML_POSITION_KEY = 'term_position'
CONTEXT_POSITION_NUMBER_KEY = 'term_position_number_key'
HTML_POSITION_NUMBER_KEY = 'term_position_number'
CONTEXT_NAME_KEY = 'name_key'
HTML_NAME_KEY = 'name'
CONTEXT_SFUID_KEY = 'sfuid_key'
HTML_SFUID_KEY = 'sfuid'
CONTEXT_EMAIL_KEY = 'email_key'
HTML_EMAIL_KEY = 'email'
CONTEXT_GMAIL_KEY = 'gmail_key'
HTML_GMAIL_KEY = 'gmail'
CONTEXT_PHONE_NUMBER_KEY = 'phone_number_key'
HTML_PHONE_NUMBER_KEY = 'phone_number'
CONTEXT_GITHUB_USERNAME_KEY = 'github_username_key'
HTML_GITHUB_USERNAME_KEY = 'github_username'
CONTEXT_COURSE1_KEY = 'course1_key'
HTML_COURSE1_KEY = 'course1'
CONTEXT_COURSE2_KEY = 'course2_key'
HTML_COURSE2_KEY = 'course2'
CONTEXT_LANGUAGE1_KEY = 'language1_key'
HTML_LANGUAGE1_KEY = 'language1'
CONTEXT_LANGUAGE2_KEY = 'language2_key'
HTML_LANGUAGE2_KEY = 'language2'
CONTEXT_BIO_KEY = 'bio_key'
HTML_BIO_KEY = 'bio'
CONTEXT_PASSPHRASE_KEY = 'passphrase_key'
HTML_PASSPHRASE_KEY = 'passphrase'
CONTEXT_PAST_OFFICERS_KEY = 'past_officers_key'
HTML_PAST_OFFICERS_KEY = 'past_officers'
CONTEXT_OFFICER_CREATION_LINKS_KEY = 'officer_creation_links_key'
HTML_OFFICER_CREATION_LINKS_KEY = 'officer_creation_links'

GITHUB_OFFICER_TEAM = "officers"
TAB_STRING = 'administration'

logger = logging.getLogger('csss_site')


def show_create_link_page(request):
    (render_value, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        return render_value
    logger.info(f"[administration/officer_views.py show_create_link_page()] request.POST={request.POST}")
    context['terms'] = ['Spring', 'Summer', 'Fall']
    context['years'] = [year for year in list(reversed(range(1970, datetime.datetime.now().year + 1)))]
    context['tab'] = 'administration'
    return render(request, 'administration/process_new_officers/show_create_link_for_officer_page.html', context)


def show_page_with_creation_links(request):
    logger.info(f"[administration/officer_views.py show_page_with_creation_links()] request.POST={request.POST}")
    logger.info(f"[administration/officer_views.py show_page_with_creation_links()] request.GET={request.GET}")
    (render_value, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        return render_value
    post_keys = [HTML_TERM_KEY, HTML_YEAR_KEY, 'positions', 'overwrite']
    if len(set(post_keys).intersection(request.POST.keys())) == len(post_keys):
        # ensuring that all the necessary keys are in the POST call
        logger.info("[administration/officer_views.py show_page_with_creation_links()] correct numbers of "
                    "request.POST keys detected")
        base_url = settings.HOST_ADDRESS + ':8000/about/allow_officer_to_choose_name?'
        officer_creation_links = []
        positions = request.POST['positions'].splitlines()
        # determines if the users that are created need to overwrite the officers for the specified term or append to
        # the list of current officers for that term
        if request.POST['overwrite'] == "true":
            position_number = 0
        elif request.POST['overwrite'] == "false":
            position_number = get_next_position_number_for_term_that_already_has_officers(request.POST['year'],
                                                                                          request.POST['term'])
        for position in positions:
            # creating links for officer inputs
            letters_and_digits = string.ascii_letters + string.digits
            newOfficerInfo = ''.join(random.choice(letters_and_digits) for i in range(10))
            newOfficerInfo = ProcessNewOfficer(
                passphrase=newOfficerInfo,
                term=request.POST[HTML_TERM_KEY],
                year=request.POST[HTML_YEAR_KEY],
                position=position,
                term_position_number=position_number
            )
            newOfficerInfo.save()
            logger.info(
                f"[administration/officer_views.py show_page_with_creation_links()] interpreting position {position}")
            link_to_create = (
                f"{base_url}passphrase={newOfficerInfo.passphrase}"
            )
            link_to_create = link_to_create.replace(" ", "%20")
            officer_creation_links.append(link_to_create)
            position_number += 1
        context['officer_creation_links'] = officer_creation_links
        return render(request, 'administration/process_new_officers/show_generated_officer_links.html', context)

    return HttpResponseRedirect('/')


def get_next_position_number_for_term_that_already_has_officers(year, term):
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
        logger.info(f"[administration/officer_views.py get_next_position_number_for_term_that_already_has_officers()] "
                    f"last officer's position number is{officers[0].term_position_number}")
        return officers[0].term_position_number + 1


def allow_officer_to_choose_name(request):
    logger.info(
        f"[administration/officer_views.py allow_officer_to_choose_name()] request.POST={request.POST}")
    (render_value, context, error_message, passphrase) = verify_passphrase_access_and_create_context(request,
                                                                                                     TAB_STRING)
    if context is None:
        request.session['error_message'] = '{}<br>'.format(error_message)
        return render_value
    context[CONTEXT_PASSPHRASE_KEY] = request.GET[HTML_PASSPHRASE_KEY]
    officers = Officer.objects.all()
    if len(officers) == 0:
        request.session['passphrase'] = "{}".format(passphrase.passphrase)
        return HttpResponseRedirect('/about/display_page_for_officer_to_input_info')
    context[HTML_PAST_OFFICERS_KEY] = officers
    return render(request, 'about/allow_officer_to_choose_name.html', context)


def display_page_for_officers_to_input_their_info(request):
    logger.info(
        f"[administration/officer_views.py display_page_for_officers_to_input_their_info()] request.GET={request.GET}")
    (render_value, context, error_message, passphrase) = verify_passphrase_access_and_create_context(request,
                                                                                                     TAB_STRING)
    if context is None:
        request.session['error_message'] = '{}<br>'.format(error_message)
        return render_value
    if "new-bio" in request.POST.keys():
        officer = None
    elif 'bio_selected' in request.POST.keys():
        officer = Officer.objects.get(id=request.POST['bio_selected'])
    else:
        officer = None
    request.session['passphrase'] = passphrase.passphrase
    context[CONTEXT_PASSPHRASE_KEY] = passphrase.passphrase
    context[HTML_PASSPHRASE_KEY] = HTML_PASSPHRASE_KEY
    context[CONTEXT_TERM_KEY] = passphrase.term
    context[HTML_TERM_KEY] = HTML_TERM_KEY
    context[CONTEXT_YEAR_KEY] = passphrase.year
    context[HTML_YEAR_KEY] = HTML_YEAR_KEY
    context[CONTEXT_POSITION_KEY] = passphrase.position
    context[HTML_POSITION_KEY] = HTML_POSITION_KEY
    context[CONTEXT_POSITION_NUMBER_KEY] = passphrase.term_position_number
    context[HTML_POSITION_NUMBER_KEY] = HTML_POSITION_NUMBER_KEY
    context[CONTEXT_NAME_KEY] = HTML_NAME_KEY
    context[HTML_NAME_KEY] = "" if officer is None else officer.name
    context[CONTEXT_SFUID_KEY] = HTML_SFUID_KEY
    context[HTML_SFUID_KEY] = "" if officer is None else officer.sfuid
    context[CONTEXT_EMAIL_KEY] = HTML_EMAIL_KEY
    context[HTML_EMAIL_KEY] = ", ".join(
        [email.email for email in AnnouncementEmailAddress.objects.filter(officer=officer)]
    )
    context[CONTEXT_GMAIL_KEY] = HTML_GMAIL_KEY
    context[HTML_GMAIL_KEY] = "" if officer is None else officer.gmail
    context[CONTEXT_PHONE_NUMBER_KEY] = HTML_PHONE_NUMBER_KEY
    context[HTML_PHONE_NUMBER_KEY] = 0 if officer is None else officer.phone_number
    context[CONTEXT_GITHUB_USERNAME_KEY] = HTML_GITHUB_USERNAME_KEY
    context[HTML_GITHUB_USERNAME_KEY] = "" if officer is None else officer.github_username
    context[CONTEXT_COURSE1_KEY] = HTML_COURSE1_KEY
    context[HTML_COURSE1_KEY] = "" if officer is None else officer.course1
    context[CONTEXT_COURSE2_KEY] = HTML_COURSE2_KEY
    context[HTML_COURSE2_KEY] = "" if officer is None else officer.course2
    context[CONTEXT_LANGUAGE1_KEY] = HTML_LANGUAGE1_KEY
    context[HTML_LANGUAGE1_KEY] = "" if officer is None else officer.language1
    context[CONTEXT_LANGUAGE2_KEY] = HTML_LANGUAGE2_KEY
    context[HTML_LANGUAGE2_KEY] = "" if officer is None else officer.language2
    context[CONTEXT_BIO_KEY] = HTML_BIO_KEY
    context[HTML_BIO_KEY] = "" if officer is None else officer.bio
    logger.info(f"[administration/officer_views.py display_page_for_officers_to_input_their_info()] context "
                f"set to '{context}'")
    logger.info(
        "[administration/officer_views.py display_page_for_officers_to_input_their_info()] returning "
        "'about/add_exec.html'")
    return render(request, 'about/add_exec.html', context)


def process_information_entered_by_officer(request):
    logger.info(
        f"[administration/officer_views.py process_information_entered_by_officer()] request.POST={request.POST}")
    post_keys = [
        HTML_TERM_KEY, HTML_YEAR_KEY, HTML_POSITION_KEY, HTML_POSITION_NUMBER_KEY, HTML_NAME_KEY,
        HTML_SFUID_KEY, HTML_EMAIL_KEY, HTML_GMAIL_KEY, HTML_PHONE_NUMBER_KEY,
        HTML_GITHUB_USERNAME_KEY, HTML_COURSE1_KEY, HTML_COURSE2_KEY, HTML_LANGUAGE1_KEY,
        HTML_LANGUAGE2_KEY, HTML_BIO_KEY, HTML_PASSPHRASE_KEY
    ]

    gdrive = GoogleDrive(settings.GDRIVE_TOKEN_LOCATION, settings.GDRIVE_ROOT_FOLDER_ID)
    if len(set(request.POST.keys()).intersection(post_keys)) == len(post_keys):
        logger.info("[administration/officer_views.py process_information_entered_by_officer()] correct number of "
                    "request.POST "
                    "keys detected")
        passphrase = ProcessNewOfficer.objects.all().filter(
            passphrase=request.POST[HTML_PASSPHRASE_KEY],
        )
        if len(passphrase) < 1 or passphrase[0].used:
            return HttpResponseRedirect('/about/bad_passphrase')
        logger.info("[administration/officer_views.py process_information_entered_by_officer()] passphrase is accurate")
        passphrase[0].used = True
        if 'passphrase' in request.session:
            del request.session['passphrase']
        passphrase[0].save()
        term_number = get_term_number(request.POST[HTML_YEAR_KEY], request.POST[HTML_TERM_KEY])
        term, created = Term.objects.get_or_create(
            term=request.POST[HTML_TERM_KEY],
            term_number=term_number,
            year=int(request.POST[HTML_YEAR_KEY])
        )
        phone_number = 0 if request.POST[HTML_PHONE_NUMBER_KEY] == '' else int(request.POST[HTML_PHONE_NUMBER_KEY])
        position_index = 0 if request.POST[HTML_POSITION_NUMBER_KEY] == '' else int(
            request.POST[HTML_POSITION_NUMBER_KEY])
        officer_position = request.POST[HTML_POSITION_KEY]
        full_name = request.POST[HTML_NAME_KEY].strip()
        full_name_in_pic = request.POST[HTML_NAME_KEY].replace(" ", "_")
        sfuid = request.POST[HTML_SFUID_KEY].strip()
        github_username = request.POST[HTML_GITHUB_USERNAME_KEY].strip()
        gmail = request.POST[HTML_GMAIL_KEY].strip()
        course1 = request.POST[HTML_COURSE1_KEY].strip()
        course2 = request.POST[HTML_COURSE2_KEY].strip()
        language1 = request.POST[HTML_LANGUAGE1_KEY].strip()
        language2 = request.POST[HTML_LANGUAGE2_KEY].strip()
        bio = request.POST[HTML_BIO_KEY].strip()
        (term_year, term_number, term_identifier) = get_term_info(term)
        pic_path = f"{settings.EXEC_PHOTOS_PATH}/{term_year}_0{term_number}_{term_identifier}/{full_name_in_pic}.jpg"

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
            "[administration/officer_views.py process_information_entered_by_officer()] "
            f"saved user term={term} full_name={full_name} officer_position={officer_position}"
        )
        post_dict = parser.parse(request.POST.urlencode())
        emails = [email.strip() for row in csv.reader(StringIO(post_dict[HTML_EMAIL_KEY]), delimiter=',') for email in row]
        for email in emails:
            save_email_to_database(email, officer)
        save_officer_github_membership(officer)
        gdrive.add_users_gdrive([gmail])
        remove_officer_from_naughty_list(full_name)
    return HttpResponseRedirect('/')


def get_term_number(year, term):
    term_number = int(year) * 10
    if term == "Spring":
        return term_number + 1
    elif term == "Summer":
        return term_number + 2
    elif term == "Fall":
        return term_number + 3


def get_term_info(term):
    term_year = term.year
    term_identifier = term.term
    if term_identifier == "Spring":
        term_number = 1
    elif term_identifier == "Summer":
        term_number = 2
    elif term_identifier == "Fall":
        term_number = 3
    else:
        term_number = -1
    return term_year, term_number, term_identifier


def save_email_to_database(email, officer_object):
    if email_is_not_in_database:
        announce_emails = AnnouncementEmailAddress(
            email=email,
            officer=officer_object
        )
        announce_emails.save()


def email_is_not_in_database(email):
    return len(AnnouncementEmailAddress.objects.filter(email=email)) == 0


def save_officer_github_membership(officer):
    github = GitHubAPI(settings.GITHUB_ACCESS_TOKEN)
    github.add_non_officer_to_a_team([officer.github_username], GITHUB_OFFICER_TEAM)
    GithubTeam(team_name=GITHUB_OFFICER_TEAM, officer=officer).save()


def remove_officer_from_naughty_list(full_name):
    naughty_officers = NaughtyOfficer.objects.all()
    for naughty_officer in naughty_officers:
        if naughty_officer.name in full_name:
            naughty_officer.delete()
            return
