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

from csss.views_helper import ERROR_MESSAGE_KEY, verify_access_logged_user_and_create_context

JSON_INPUT_POST_KEY = 'input_json'

JSON_YEAR_KEY = 'year'
JSON_TERM_KEY = 'term'

JSON_OFFICER_KEY = 'officers'

TAB_STRING = 'administration'

logger = logging.getLogger('csss_site')


def create_link(request):
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(
        request,
        TAB_STRING
    )
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    post_keys = ['term', 'year', 'positions', 'overwrite']
    logger.info(f"[administration/views.py create_link()] request.POST={request.POST}")
    logger.info(f"[administration/views.py create_link()] request.GET={request.GET}")
    if len(request.POST.keys()) == (len(post_keys) + 1):
        logger.info("[administration/views.py create_link()] correct numbers of request.POST keys detected")
        for key in request.POST.keys():
            if key not in post_keys:
                logger.info(f"[administration/views.py create_link()] invalid key '{key}' detected")

        base_url = settings.HOST_ADDRESS + '/about/input_officer_info?'
        officer_links = []
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
            officer_links.append(link_to_create)
            position_number += 1
        context.update({'officer_links': officer_links})
        return render(request, 'administration/show_generated_officer_links.html', context)

    return HttpResponseRedirect(f"{settings.URL_ROOT}")


def show_create_link_page(request):
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(
        request,
        TAB_STRING
    )
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    context.update({
        'terms': ['Spring', 'Summer', 'Fall'],
        'years': [b for b in list(reversed(range(1970, datetime.datetime.now().year+1)))],
    })
    return render(request, 'administration/show_create_link_for_officer_page.html', context)


def create_or_update_specified_term_with_provided_json(request):
    logger.info(
        "[administration/views.py create_or_update_specified_term_with_provided_json()] "
        f"[create_or_update_specified_term_with_provided_json] request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(
        request,
        TAB_STRING
    )
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
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
        save_officers_from_json(post_dict[JSON_OFFICER_KEY], term)

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
JSON_OFFICER_POSITION_KEY = 'officer_position'


def save_officers_from_json(officers, term):
    position_index = 0
    for officer in officers:
        officer_position = officer[JSON_OFFICER_POSITION_KEY]
        full_name = officer[JSON_NAME_KEY]
        sfuid = officer[JSON_SFUID_KEY]
        phone_number = officer[JSON_PHONE_NUMBER_KEY]
        github = officer[JSON_GITHUB_USERNAME_KEY]
        gmail = officer[JSON_GMAIL_KEY]
        course1 = officer[JSON_COURSE1_KEY]
        course2 = officer[JSON_COURSE2_KEY]
        language1 = officer[JSON_LANGUAGE1_KEY]
        language2 = officer[JSON_LANGUAGE2_KEY]
        bio = officer[JSON_BIO_KEY]
        pic_path = officer[JSON_PIC_PATH_KEY]

        logger.info(
            "[administration/views.py save_officers_from_json()] "
            f"saved user term={term} full_name={full_name} officer_position={officer_position}"
        )
        officer = Officer(
            position=officer_position,
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

        for email in officer[JSON_ANNOUNCEMENT_EMAILS_KEY]:
            announce_emails = AnnouncementEmailAddress(
                email=email,
                officer=officer
            )
            announce_emails.save()
        position_index += 1
