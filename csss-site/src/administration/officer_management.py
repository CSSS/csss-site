import datetime
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
import json
import logging
from querystring_parser import parser
from about.models import Term, Officer, AnnouncementEmailAddress
from administration.models import OfficerUpdatePassphrase
import random
import string

JSON_INPUT_POST_KEY = 'input_json'

JSON_YEAR_KEY = 'year'
JSON_TERM_KEY = 'term'

JSON_EXEC_KEY = 'execs'

logger = logging.getLogger('csss_site')


def create_link(request):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'administration',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': "/"+settings.URL_ROOT
    }
    if not (request.user.is_staff or 'Exec' in groups):
        return render(request, 'administration/invalid_access.html', context)

    post_keys = ['term', 'year', 'positions', 'overwrite']
    logger.info(f"[administration/views.py create_link()] request.POST={request.POST}")
    logger.info(f"[administration/views.py create_link()] request.GET={request.GET}")
    if len(request.POST.keys()) == (len(post_keys) + 1):
        logger.info("[administration/views.py create_link()] correct numbers of request.POST keys detected")
        for key in request.POST.keys():
            if key not in post_keys:
                logger.info(f"[administration/views.py create_link()] invalid key '{key}' detected")

        base_url = settings.HOST_ADDRESS + '/about/input_exec_info?'
        exec_links = []
        positions = request.POST['positions'].splitlines()
        if request.POST['overwrite'] == "true":
            position_number = 0
        elif request.POST['overwrite'] == "false":
            term_number = int(request.POST['year']) * 10
            if request.POST['term'] == "Spring":
                term_number = term_number + 1
            elif request.POST['term'] == "Summer":
                term_number = term_number + 2
            elif request.POST['term'] == "Fall":
                term_number = term_number + 3
            term = Term.objects.filter(
                year=request.POST['year'],
                term=request.POST['term'],
                term_number=term_number
            )
            if len(term) < 1:
                position_number = 0
            else:
                officers = Officer.objects.all().filter(
                    elected_term=term[0]
                ).order_by('-term_position_number')
                logger.info(f"[administration/views.py] create_link()] officers={officers[0]}")
                position_number = officers[0].term_position_number+1
        for position in positions:
            letters_and_digits = string.ascii_letters + string.digits
            passphrase = ''.join(random.choice(letters_and_digits) for i in range(10))
            passphrase = OfficerUpdatePassphrase(passphrase=passphrase)
            passphrase.save()
            logger.info(f"[administration/views.py create_link()] interpreting position {position}")
            link_to_create = (
                f"{base_url}term={request.POST['term']}&year={request.POST['year']}&"
                f"position={position}&position_number={position_number}&passphrase={passphrase.passphrase}"
            )
            link_to_create = link_to_create.replace(" ", "%20")
            exec_links.append(link_to_create)
            position_number += 1
        context.update({'exec_links': exec_links})
        return render(request, 'administration/show_generated_officer_links.html', context)

    return HttpResponseRedirect('/')


def show_create_link_page(request):
    terms = ['Spring', 'Summer', 'Fall']
    years = [b for b in list(reversed(range(1970, datetime.datetime.now().year+1)))]
    groups = list(request.user.groups.values_list('name', flat=True))

    context = {
        'tab': 'administration',
        'authenticated': request.user.is_authenticated,
        'terms': terms,
        'years': years,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': "/"+settings.URL_ROOT
    }
    if not (request.user.is_staff or 'Exec' in groups):
        return render(request, 'administration/invalid_access.html', context)
    return render(request, 'administration/show_create_link_for_officer_page.html', context)


def create_or_update_specified_term_with_provided_json(request):
    logger.info(
        "[administration/views.py create_or_update_specified_term_with_provided_json()] "
        f"[create_or_update_specified_term_with_provided_json] request.POST={request.POST}"
    )
    groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'tab': 'administration',
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'URL_ROOT': "/"+settings.URL_ROOT
    }
    if not (request.user.is_staff or 'Exec' in groups):
        return render(request, 'administration/invalid_access.html', context)
    if JSON_INPUT_POST_KEY in request.POST:
        logger.info(
            "[administration/views.py create_or_update_specified_term_with_provided_json()] creating new election"
        )
        post_dict = parser.parse(request.POST.urlencode())
        post_dict = json.loads(request.POST['input_json'])
        logger.info(
            f"[administration/views.py create_or_update_specified_term_with_provided_json()] post_dict={post_dict}"
        )
        term = get_term_json(json.loads(request.POST['input_json']))
        # post_dict = parser.parse(request.POST.urlencode())
        logger.info(
            f"[administration/views.py create_or_update_specified_term_with_provided_json()] post_dict={post_dict}"
        )
        save_execs_from_json(post_dict[JSON_EXEC_KEY], term)

        return render(request, 'administration/update_officers_for_term_json.html', context)
    return render(request, 'administration/update_officers_for_term_json.html', context)


def get_term_json(input_json):
    year = input_json[JSON_YEAR_KEY]
    term = input_json[JSON_TERM_KEY]
    term_number = int(year) * 10
    if term == "Spring":
        term_number = term_number + 1
    elif term == "Summer":
        term_number = term_number + 2
    elif term == "Fall":
        term_number = term_number + 3
    Term.objects.filter(
        term=term,
        term_number=term_number,
        year=year
    ).delete()

    term = Term(
        term=term,
        term_number=term_number,
        year=year,
    )
    term.save()
    logger.info(f"[administration/views.py get_term_json()] term {term} created")
    return term


JSON_NAME_KEY = 'name'
JSON_SFUID_KEY = 'sfuid'
JSON_ANNOUNCEMENT_EMAILS_KEY = 'announcement_emails'
JSON_PHONE_NUMBER_KEY = 'phone_number'
JSON_GITHUB_USERNAME_KEY = 'github_username'
JSON_GMAIL_KEY = 'gmail'
JSON_COURSE1_KEY = 'fav_course_1'
JSON_COURSE2_KEY = 'fav_course_2'
JSON_LANGUAGE1_KEY = 'fav_language_1'
JSON_LANGUAGE2_KEY = 'fav_language_2'
JSON_BIO_KEY = 'bio'
JSON_PIC_PATH_KEY = 'profile_pic_path'
JSON_EXEC_POSITION_KEY = 'exec_position'


def save_execs_from_json(execs, term):
    position_index = 0
    for exec in execs:
        exec_position = exec[JSON_EXEC_POSITION_KEY]
        full_name = exec[JSON_NAME_KEY]
        sfuid = exec[JSON_SFUID_KEY]
        phone_number = exec[JSON_PHONE_NUMBER_KEY]
        github = exec[JSON_GITHUB_USERNAME_KEY]
        gmail = exec[JSON_GMAIL_KEY]
        course1 = exec[JSON_COURSE1_KEY]
        course2 = exec[JSON_COURSE2_KEY]
        language1 = exec[JSON_LANGUAGE1_KEY]
        language2 = exec[JSON_LANGUAGE2_KEY]
        bio = exec[JSON_BIO_KEY]
        pic_path = exec[JSON_PIC_PATH_KEY]

        logger.info(
            "[administration/views.py save_execs_from_json()] "
            f"saved user term={term} full_name={full_name} exec_position={exec_position}"
        )
        officer = Officer(
            position=exec_position,
            term_position_number=position_index,
            name=full_name,
            sfuid=sfuid,
            phone_number=phone_number,
            github_username=github,
            gmail=gmail,
            course1=course1,
            course2=course2,
            language1=language1,
            language2=language2,
            bio=bio,
            elected_term=term,
            image=pic_path
        )
        officer.save()

        for email in exec[JSON_ANNOUNCEMENT_EMAILS_KEY]:
            announce_emails = AnnouncementEmailAddress(
                email=email,
                officer=officer
            )
            announce_emails.save()
        position_index += 1
