import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from about.models import NewOfficer, Officer
from about.views.Constants import STRING_PREPENDED_TO_SEND_LINK_TO_OFFICER_BUTTON
from about.views.create_context.input_new_officers.create_context_for_specify_new_officers_html import \
    create_context_for_specify_new_officers_html
from about.views.input_new_officers.discord_dms.dm_new_officers_on_discord import dm_new_officers_on_discord
from about.views.input_new_officers.specify_new_officers.save_new_officers import save_new_officers
from about.views.input_new_officers.specify_new_officers.utils.ensure_term_info_are_present import \
    ensure_term_info_are_present
from about.views.input_new_officers.specify_new_officers.utils.transform_webform_to_json import \
    transform_webform_to_json
from about.views.input_new_officers.specify_new_officers.validators.validate_inputted_new_officers import \
    validate_inputted_new_officers
from about.views.input_new_officers.specify_new_officers.validators.validate_inputted_term_info import \
    validate_inputted_term_info
from about.views.input_new_officers.specify_new_officers.validators.validate_user_command import validate_user_command
from csss.settings import URL_ROOT

logger = logging.getLogger('csss_site')


def process_specified_new_officers(request, context):
    """
    Takes in the New Officer inputs and validated it before saving it and then DMing those users to get them to
    fill in the form

    Keyword Arguments
    request -- the django request object that the new officers are contained in
    context -- the dictionary that needs to be filled in with the user's input and the error message if there
     was an error

    Return
    either redirect the user back to tha page where they entered the new officers infos, either asking for a
     correction or just to display the saved data
    """
    new_officers, inputted_term, inputted_year, id_of_new_officer_to_send_link_to, save_or_update_new_officers = \
        transform_webform_to_json(
            parser.parse(request.POST.urlencode())
        )
    save_or_update_new_officers = validate_user_command(save_or_update_new_officers)
    if not (id_of_new_officer_to_send_link_to is not None or save_or_update_new_officers):
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
    if len(new_officers) == 0:
        # if the user submitted a form that has no new officers.
        NewOfficer.objects.all().delete()
    elif id_of_new_officer_to_send_link_to is not None:
        # if the user clicked the button to send a discord DM to a particular new Officer
        new_officer_to_dm = NewOfficer.objects.all().filter(id=id_of_new_officer_to_send_link_to).first()
        if new_officer_to_dm is not None:
            first_time_officer = (
                Officer.objects.all().filter(sfuid=new_officer_to_dm.sfu_computing_id).first() is None
            )
            success, error_message = dm_new_officers_on_discord(
                new_officer_to_dm.full_name, new_officer_to_dm.discord_id, first_time_officer
            )

            # below logic is here so that if the user hit the button mid-draft, the DM get sent but the
            # draft is preserved
            create_context_for_specify_new_officers_html(
                context, error_messages=[error_message],
                term=inputted_term, year=inputted_year,
                draft_new_officers=new_officers
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
                context, error_messages=[error_message],
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
        success, error_message = validate_inputted_new_officers(inputted_term, inputted_year, new_officers)
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
        success, error_message = save_new_officers(inputted_term, inputted_year, new_officers)
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
    return HttpResponseRedirect(f'{URL_ROOT}about/specify_new_officers')
