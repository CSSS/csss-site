import logging

from django.conf import settings
from django.shortcuts import render

from about.views.create_context.enter_officer_info.create_context_for_enter_officer_info_html import \
    create_context_for_enter_officer_info_html
from about.views.input_new_officers.enter_officer_info.save_new_officer import save_new_officer
from about.views.input_new_officers.enter_officer_info.validators.validate_announcement_emails import \
    validate_announcement_emails
from about.views.input_new_officers.enter_officer_info.validators.validate_github_username import \
    validate_github_username
from about.views.input_new_officers.enter_officer_info.validators.validate_gmail import validate_gmail
from about.views.input_new_officers.enter_officer_info.validators.validate_gmail_code import validate_gmail_code
from about.views.input_new_officers.enter_officer_info.validators.validate_phone_number import validate_phone_number

logger = logging.getLogger('csss_site')


def process_specified_new_officer_info(request, context, new_officer=None):
    # {
    #     'csrfmiddlewaretoken': ['TRirgh4NZRXyWdHYR4tENwSgsuRM82V0mTJKa2YWfGQnWCGkdI5l4LOeO2JzH7Ox'],
    #     'term': ['Spring'],
    #     'year': ['2022'],
    #     'term_position': ['Systems Administrator'],
    #     'date': ['Dec. 28, 2021, midnight'],
    #     'position_index': [''],
    #     'sfu_email_list_address': [''],
    #     'name': ['Jace Manshadi'], <-- grab
    #     'sfuid': ['jsaadatm'],
    #     'sfuid_email_alias': ['j_manshad'],
    #     'announcement_emails': [''], <-- grab
    #     'gmail': ['jaymanshadi@gmail.com'], <-- grab
    #     'phone_number': ['0'], <-- grab
    #     'github_username': ['modernNeo'] <-- grab,
    #     'course1': ['CMPT 433'], <-- grab
    #     'course2': ['CMPT 471'], <-- grab
    #     'language1': ['C++'], <-- grab
    #     'language2': ['Assembly'], <-- grab
    #     'bio': ['just here to have fun with python and jenkins'] <-- grab
    # }
    new_officer_info = {
        "name": request.POST.get("name", None),
        "announcement_emails": request.POST.get("announcement_emails", None),
        "gmail": request.POST.get("gmail", None),
        "gmail_code": request.POST.get("gmail_code", None),
        "phone_number": request.POST.get("phone_number", None),
        "github_username": request.POST.get("github_username", None),
        "course1": request.POST.get("course1", None),
        "course2": request.POST.get("course2", None),
        "language1": request.POST.get("language1", None),
        "language2": request.POST.get("language2", None),
        "bio": request.POST.get("bio", None),
    }
    success, error_message = validate_announcement_emails(new_officer_info['announcement_emails'])
    if not success:
        error_message = "One of the announcement emails is invalid"
        logger.info(
            f"[about/process_specified_new_officer_info.py process_specified_new_officer_info()] {error_message}"
        )
        create_context_for_enter_officer_info_html(
            request, context, new_officer=new_officer, new_officer_info=new_officer_info
        )
        return render(request, 'about/input_new_officers/enter_officer_info.html', context)
    success, error_message = validate_gmail(new_officer_info['gmail'])
    if not success:
        error_message = "Invalid gmail"
        logger.info(
            f"[about/process_specified_new_officer_info.py process_specified_new_officer_info()] {error_message}"
        )
        create_context_for_enter_officer_info_html(
            request, context, new_officer=new_officer, new_officer_info=new_officer_info
        )
        return render(request, 'about/input_new_officers/enter_officer_info.html', context)
    success, error_message = validate_gmail_code(new_officer_info['gmail_code'], new_officer=new_officer)
    if not success:
        error_message = "Invalid gmail"
        logger.info(
            f"[about/process_specified_new_officer_info.py process_specified_new_officer_info()] {error_message}"
        )
        create_context_for_enter_officer_info_html(
            request, context, new_officer=new_officer, new_officer_info=new_officer_info
        )
        return render(request, 'about/input_new_officers/enter_officer_info.html', context)
    success, error_message = validate_phone_number(new_officer_info['phone_number'])
    if not success:
        error_message = "Invalid phone number"
        logger.info(
            f"[about/process_specified_new_officer_info.py process_specified_new_officer_info()] {error_message}"
        )
        create_context_for_enter_officer_info_html(
            request, context, new_officer=new_officer, new_officer_info=new_officer_info
        )
        return render(request, 'about/input_new_officers/enter_officer_info.html', context)
    success, error_message = validate_github_username(new_officer_info['github_username'])
    if not success:
        error_message = "Github username is invalid"
        logger.info(
            f"[about/process_specified_new_officer_info.py process_specified_new_officer_info()] {error_message}"
        )
        create_context_for_enter_officer_info_html(
            request, context, new_officer=new_officer, new_officer_info=new_officer_info
        )
        return render(request, 'about/input_new_officers/enter_officer_info.html', context)
    save_new_officer(new_officer_info)
    return HttpResponseRedirect(f"{settings.URL_ROOT}about/list_of_current_officers")
