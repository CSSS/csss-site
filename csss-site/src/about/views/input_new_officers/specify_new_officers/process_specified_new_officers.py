import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from about.views.Constant_v2 import NEW_OFFICERS__HTML_VALUE, ID_KEY, TERM_KEY, YEAR_KEY
from about.views.create_context.specify_new_officers.create_context_for_specify_new_officers_html import \
    create_context_for_specify_new_officers_html
from about.views.input_new_officers.specify_new_officers.save_new_officers import save_new_officers
from about.views.input_new_officers.specify_new_officers.validators.validate_inputted_new_officers import \
    validate_inputted_new_officers
from about.views.input_new_officers.specify_new_officers.validators.validate_inputted_term_info import \
    validate_inputted_term_info
from about.views.input_new_officers.specify_new_officers.validators.validate_user_command import validate_user_command
from csss.settings import URL_ROOT
from elections.views.validators.validate_user_input_has_required_fields import verify_user_input_has_all_required_fields

logger = logging.getLogger('csss_site')


def process_specified_new_officers(request, context):
    new_officers_dict = parser.parse(request.POST.urlencode())
    new_officers = []
    if NEW_OFFICERS__HTML_VALUE in new_officers_dict and type(new_officers_dict[NEW_OFFICERS__HTML_VALUE]) == dict:
        new_officers = list(new_officers_dict[NEW_OFFICERS__HTML_VALUE].values())
        for new_officer in new_officers:
            if ID_KEY in new_officer and len(new_officer[ID_KEY]) == 0:
                del new_officer[ID_KEY]
    fields = [TERM_KEY, YEAR_KEY, "save_or_update_new_officers"]
    error_message = verify_user_input_has_all_required_fields(new_officers_dict, fields=fields)
    if error_message != "":
        logger.info(
            f"[about/process_specified_new_officers.py process_specified_new_officers()] {error_message}"
        )
        create_context_for_specify_new_officers_html(
            context, error_messages=[error_message]
        )
        return render(request, 'about/input_new_officers/specify_new_officers.html', context)
    inputted_term = new_officers_dict[TERM_KEY]
    inputted_year = new_officers_dict[YEAR_KEY]
    save_or_update_new_officers = new_officers_dict['save_or_update_new_officers']
    if not validate_user_command(save_or_update_new_officers):
        error_message = "Unable to understand user command"
        logger.info(
            f"[about/process_specified_new_officers.py process_specified_new_officers()] {error_message}"
        )
        create_context_for_specify_new_officers_html(
            context, error_messages=[error_message],
            term=inputted_term, year=inputted_year,
            draft_new_officers=new_officers
        )
        return render(request, 'about/input_new_officers/specify_new_officers.html', context)
    success, error_message = validate_inputted_term_info(inputted_term, inputted_year)
    if not success:
        logger.info(
            f"[about/process_specified_new_officers.py process_specified_new_officers()] {error_message}"
        )
        create_context_for_specify_new_officers_html(
            context, error_messages=[error_message],
            term=inputted_term, year=inputted_year,
            draft_new_officers=new_officers
        )
        return render(request, 'about/input_new_officers/specify_new_officers.html', context)
    success, error_message = validate_inputted_new_officers(new_officers)
    if not success:
        logger.info(
            f"[about/process_specified_new_officers.py process_specified_new_officers()] {error_message}"
        )
        create_context_for_specify_new_officers_html(
            context, error_messages=[error_message],
            term=inputted_term, year=inputted_year,
            draft_new_officers=new_officers
        )
        return render(request, 'about/input_new_officers/specify_new_officers.html', context)
    save_new_officers(inputted_term, inputted_year, new_officers)
    return HttpResponseRedirect(f'{URL_ROOT}about/specify_new_officers')
