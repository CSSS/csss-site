import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render

from about.views.Constants import UNPROCESSED_OFFICER_NAME__KEY, UNPROCESSED_OFFICER_PHONE_NUMBER_KEY, \
    UNPROCESSED_OFFICER_COURSE_1__KEY, \
    UNPROCESSED_OFFICER_COURSE_2__KEY, UNPROCESSED_OFFICER_LANGUAGE_1__KEY, \
    UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__KEY, UNPROCESSED_OFFICER_LANGUAGE_2__KEY, \
    UNPROCESSED_OFFICER_BIO__KEY, UNPROCESSED_OFFICER_GITHUB_USERNAME__KEY, UNPROCESSED_OFFICER_GMAIL__KEY, \
    UNPROCESSED_OFFICER_GMAIL_VERIFICATION_CODE__HTML_VALUE, \
    RE_SEND_GMAIL_VERIFICATION_CODE
from about.views.create_context.input_new_officers.enter_new_officer_info.\
    create_context_for_enter_new_officer_info_html import \
    create_context_for_enter_new_officer_info_html
from about.views.input_new_officers.enter_new_officer_info.save_officer_and_grant_digital_resources import \
    save_officer_and_grant_digital_resources
from about.views.input_new_officers.enter_new_officer_info.utils.transform_webform_to_json import \
    transform_webform_to_json
from about.views.input_new_officers.enter_new_officer_info.validators.validate_gmail import validate_gmail
from about.views.input_new_officers.enter_new_officer_info.validators.validate_user_info import validate_user_info
from csss.settings import URL_ROOT
from csss.views_helper import verify_user_input_has_all_required_fields

logger = logging.getLogger('csss_site')


def process_new_officer_info(request, context, officer_emaillist_and_position_mappings, unprocessed_officers):
    """
    Processed the user's input of their info that will display on the list of current officers

    Keyword Argument
    request -- django request object
    context -- the context dictionary
    officer_emaillist_and_position_mappings -- the queryset of currently saved position infos
    unprocessed_officers -- the queryset of currently saved unprocessed officers

    Return
    render object that either directs user back to the page for entering their info if there was an error or
     just to the index page
    """
    unprocessed_officer = unprocessed_officers.filter(sfu_computing_id=request.user.username).first()
    position_info = officer_emaillist_and_position_mappings.filter(
        position_name=unprocessed_officer.position_name
    ).first()
    github_team_to_add = position_info.officerpositiongithubteammapping_set.all()

    officer_info = transform_webform_to_json(request.POST)
    fields = [
        UNPROCESSED_OFFICER_NAME__KEY, UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__KEY,
        UNPROCESSED_OFFICER_PHONE_NUMBER_KEY, UNPROCESSED_OFFICER_COURSE_1__KEY,
        UNPROCESSED_OFFICER_COURSE_2__KEY, UNPROCESSED_OFFICER_LANGUAGE_1__KEY, UNPROCESSED_OFFICER_LANGUAGE_2__KEY,
        UNPROCESSED_OFFICER_BIO__KEY
    ]

    if len(github_team_to_add) > 0:
        fields.append(UNPROCESSED_OFFICER_GITHUB_USERNAME__KEY)
    if position_info.google_drive:
        fields.append(UNPROCESSED_OFFICER_GMAIL__KEY)
    error_message = verify_user_input_has_all_required_fields(officer_info, fields)
    if error_message != "":
        logger.info(
            "[about/process_new_officer_info.py"
            f" process_new_officer_info()] {error_message}"
        )
        create_context_for_enter_new_officer_info_html(
            context, request.user.username, officer_emaillist_and_position_mappings, unprocessed_officers,
            officer_info=officer_info, error_messages=[error_message],
            position_info=position_info
        )
        return render(request, 'about/input_new_officers/enter_new_officer_info/enter_new_officer_info.html', context)
    success, error_message = validate_user_info(officer_info)
    if not success:
        logger.info(
            "[about/process_new_officer_info.py"
            f" process_new_officer_info()] {error_message}"
        )
        create_context_for_enter_new_officer_info_html(
            context, request.user.username, officer_emaillist_and_position_mappings, unprocessed_officers,
            officer_info=officer_info, error_messages=[error_message],
            position_info=position_info
        )
        return render(request, 'about/input_new_officers/enter_new_officer_info/enter_new_officer_info.html', context)
    success, error_message = validate_gmail(
        unprocessed_officers, unprocessed_officer, officer_info[UNPROCESSED_OFFICER_GMAIL__KEY],
        officer_info[UNPROCESSED_OFFICER_GMAIL_VERIFICATION_CODE__HTML_VALUE],
        resend_verification_code=officer_info[RE_SEND_GMAIL_VERIFICATION_CODE]
    )
    if not success:
        if error_message is None:
            create_context_for_enter_new_officer_info_html(
                context, request.user.username, officer_emaillist_and_position_mappings, unprocessed_officers,
                officer_info=officer_info, position_info=position_info
            )
        else:
            logger.info(
                "[about/process_new_officer_info.py"
                f" process_new_officer_info()] {error_message}"
            )
            create_context_for_enter_new_officer_info_html(
                context, request.user.username, officer_emaillist_and_position_mappings, unprocessed_officers,
                officer_info=officer_info, error_messages=[error_message],
                position_info=position_info
            )
        return render(request, 'about/input_new_officers/enter_new_officer_info/enter_new_officer_info.html',
                      context)
    success, error_message = save_officer_and_grant_digital_resources(
        officer_emaillist_and_position_mappings, unprocessed_officer, officer_info
    )
    if not success:
        logger.info(
            "[about/process_new_officer_info.py"
            f" process_new_officer_info()] {error_message}"
        )
        create_context_for_enter_new_officer_info_html(
            context, request.user.username, officer_emaillist_and_position_mappings, unprocessed_officers,
            officer_info=officer_info, error_messages=[error_message], position_info=position_info
        )
        return render(request, 'about/input_new_officers/enter_new_officer_info/enter_new_officer_info.html', context)
    unprocessed_officer.delete()
    return HttpResponseRedirect(f"{URL_ROOT}about/list_of_current_officers")
