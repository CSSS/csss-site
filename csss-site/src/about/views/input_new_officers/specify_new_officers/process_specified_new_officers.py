import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from about.models import Officer, Term
from about.views.create_context.input_new_officers.create_context_for_specify_new_officers_html import \
    create_context_for_specify_new_officers_html
from about.views.input_new_officers.specify_new_officers.notifications.\
    send_notification_asking_officer_to_fill_in_form import \
    send_notification_asking_officer_to_fill_in_form
from about.views.input_new_officers.specify_new_officers.save_unprocessed_officers import save_unprocessed_officers
from about.views.input_new_officers.specify_new_officers.utils.ensure_term_info_are_present import \
    ensure_term_info_are_present
from about.views.input_new_officers.specify_new_officers.utils.transform_webform_to_json import \
    transform_webform_to_json
from about.views.input_new_officers.specify_new_officers.validators.validate_inputted_term_info import \
    validate_inputted_term_info
from about.views.input_new_officers.specify_new_officers.validators.validate_inputted_unprocessed_officers import \
    validate_inputted_unprocessed_officers
from about.views.input_new_officers.specify_new_officers.validators.validate_user_command import validate_user_command
from csss.settings import URL_ROOT

logger = logging.getLogger('csss_site')


def process_specified_new_officers(
        request, context, saved_unprocessed_officers, officer_emaillist_and_position_mappings):
    """
    Takes in the New Officer inputs and validated it before saving it and then DMing those users to get them to
    fill in the form

    Keyword Arguments
    request -- the django request object that the new officers are contained in
    context -- the dictionary that needs to be filled in with the user's input and the error message if there
     was an error
    saved_unprocessed_officers -- the queryset of currently saved unprocessed officers
    officer_emaillist_and_position_mappings -- the queryset of currently saved position infos

    Return
    either redirect the user back to tha page where they entered the new officers infos, either asking for a
     correction or just to display the saved data
    """
    values = transform_webform_to_json(parser.parse(request.POST.urlencode()))
    officers = Officer.objects.all()
    terms = Term.objects.all()
    unprocessed_officers = values[0]
    inputted_term = values[1]
    inputted_year = values[2]
    id_of_new_officer_to_send_link_to = values[3]
    save_or_update_new_officers = values[4]
    save_or_update_new_officers_option_selected = validate_user_command(save_or_update_new_officers)
    if not (id_of_new_officer_to_send_link_to is not None or save_or_update_new_officers_option_selected):
        error_message = "Unable to understand user command"
        logger.info(
            f"[about/process_specified_new_officers.py process_specified_new_officers()] {error_message}"
        )
        create_context_for_specify_new_officers_html(
            context, saved_unprocessed_officers, officer_emaillist_and_position_mappings,
            error_messages=[error_message], term=inputted_term, year=inputted_year,
            draft_new_officers=unprocessed_officers
        )
        return render(request, 'about/input_new_officers/specify_new_officers.html', context)
    if len(unprocessed_officers) == 0:
        # if the user submitted a form that has no new officers.
        saved_unprocessed_officers.delete()
    elif id_of_new_officer_to_send_link_to is not None:
        # if the user clicked the button to send a discord DM to a particular new Officer
        new_officer_to_dm = saved_unprocessed_officers.filter(id=id_of_new_officer_to_send_link_to).first()
        if new_officer_to_dm is not None:
            first_time_officer = (
                Officer.objects.all().filter(sfu_computing_id=new_officer_to_dm.sfu_computing_id).first() is None
            )
            success, error_message = send_notification_asking_officer_to_fill_in_form(
                new_officer_to_dm.discord_id, new_officer_to_dm.full_name, first_time_officer
            )

            # below logic is here so that if the user hit the button mid-draft, the DM get sent but the
            # draft is preserved
            create_context_for_specify_new_officers_html(
                context, saved_unprocessed_officers, officer_emaillist_and_position_mappings,
                error_messages=[error_message], term=inputted_term, year=inputted_year,
                draft_new_officers=unprocessed_officers
            )
            return render(request, 'about/input_new_officers/specify_new_officers.html', context)
    else:
        # user submitted New_Officer info that has to be parsed
        success, error_message = ensure_term_info_are_present(inputted_term, inputted_year)
        if not success:
            logger.info(
                f"[about/process_specified_new_officers.py process_specified_new_officers()] {error_message}"
            )
            create_context_for_specify_new_officers_html(
                context, saved_unprocessed_officers, officer_emaillist_and_position_mappings,
                error_messages=[error_message], draft_new_officers=unprocessed_officers
            )
            return render(request, 'about/input_new_officers/specify_new_officers.html', context)
        success, error_message = validate_inputted_term_info(inputted_term, inputted_year)
        if not success:
            logger.info(
                f"[about/process_specified_new_officers.py process_specified_new_officers()] {error_message}"
            )
            create_context_for_specify_new_officers_html(
                context, saved_unprocessed_officers, officer_emaillist_and_position_mappings,
                error_messages=[error_message], term=inputted_term, year=inputted_year,
                draft_new_officers=unprocessed_officers
            )
            return render(request, 'about/input_new_officers/specify_new_officers.html', context)
        success, error_message = validate_inputted_unprocessed_officers(
            saved_unprocessed_officers, officer_emaillist_and_position_mappings, officers, terms, inputted_term,
            inputted_year, unprocessed_officers=unprocessed_officers
        )
        if not success:
            logger.info(
                f"[about/process_specified_new_officers.py process_specified_new_officers()] {error_message}"
            )
            create_context_for_specify_new_officers_html(
                context, saved_unprocessed_officers, officer_emaillist_and_position_mappings,
                error_messages=[error_message], term=inputted_term, year=inputted_year,
                draft_new_officers=unprocessed_officers
            )
            return render(request, 'about/input_new_officers/specify_new_officers.html', context)
        success, error_message = save_unprocessed_officers(
            saved_unprocessed_officers, officer_emaillist_and_position_mappings, officers, terms, inputted_term,
            inputted_year, unprocessed_officers
        )
        if not success:
            logger.info(
                f"[about/process_specified_new_officers.py process_specified_new_officers()] {error_message}"
            )
            create_context_for_specify_new_officers_html(
                context, saved_unprocessed_officers, officer_emaillist_and_position_mappings,
                error_messages=[error_message], term=inputted_term, year=inputted_year,
                draft_new_officers=unprocessed_officers
            )
            return render(request, 'about/input_new_officers/specify_new_officers.html', context)
    return HttpResponseRedirect(f'{URL_ROOT}about/specify_new_officers')
