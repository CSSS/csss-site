import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from about.models import Term, NewOfficer
from about.views.create_context.specify_new_officers.create_context_for_specify_new_officers_html import \
    create_context_for_specify_new_officers_html
from about.views.input_new_officers.save_new_officers import save_new_officers
from about.views.input_new_officers.validators.validate_inputted_new_officers import validate_inputted_new_officers
from about.views.input_new_officers.validators.validate_inputted_term_info import validate_inputted_term_info
from about.views.input_new_officers.validators.validate_user_command import validate_user_command
from csss.settings import URL_ROOT
from elections.views.validators.validate_user_input_has_required_fields import verify_user_input_has_all_required_fields

logger = logging.getLogger('csss_site')


def process_specified_new_officers(request, context):
    if 'delete_all_new_officers' in request.POST and request.POST['delete_all_new_officers'] == "Delete All New Officers":
        NewOfficer.objects.all().delete()
        return HttpResponseRedirect(f'{URL_ROOT}about/specify_new_officers')

    new_officers_dict = parser.parse(request.POST.urlencode())
    # new_officers_dict = parser.parse("csrfmiddlewaretoken=MhjctIRKYbki8yIaTA1dn0jwzfWJThGOPG5rqjDqEdeDeWZQj5rCvuLRYmBT8kW5&term=Spring&year=2022&%5Bnew_officers%5D%5B0%5D%5Bselected_position%5D=President&%5Bnew_officers%5D%5B0%5D%5Bdiscord_id%5D=265690903543283712&%5Bnew_officers%5D%5B0%5D%5Bsfu_computing_id%5D=mgale&%5Bnew_officers%5D%5B0%5D%5Bre_use_start_date%5D=on&%5Bnew_officers%5D%5B1%5D%5Bselected_position%5D=Vice-President&%5Bnew_officers%5D%5B1%5D%5Bdiscord_id%5D=265690903543283712&%5Bnew_officers%5D%5B1%5D%5Bsfu_computing_id%5D=ssanei&%5Bnew_officers%5D%5B1%5D%5Bre_use_start_date%5D=on&%5Bnew_officers%5D%5B2%5D%5Bselected_position%5D=Treasurer&%5Bnew_officers%5D%5B2%5D%5Bdiscord_id%5D=183358777444007936&%5Bnew_officers%5D%5B2%5D%5Bsfu_computing_id%5D=ablondal&%5Bnew_officers%5D%5B2%5D%5Bre_use_start_date%5D=on&%5Bnew_officers%5D%5B3%5D%5Bselected_position%5D=Director+of+Resources&%5Bnew_officers%5D%5B3%5D%5Bdiscord_id%5D=124044674372599808&%5Bnew_officers%5D%5B3%5D%5Bsfu_computing_id%5D=trumanb&%5Bnew_officers%5D%5B3%5D%5Bre_use_start_date%5D=on&%5Bnew_officers%5D%5B4%5D%5Bselected_position%5D=Director+of+Events&%5Bnew_officers%5D%5B4%5D%5Bdiscord_id%5D=264645255427522560&%5Bnew_officers%5D%5B4%5D%5Bsfu_computing_id%5D=ckl47&%5Bnew_officers%5D%5B4%5D%5Bre_use_start_date%5D=on&%5Bnew_officers%5D%5B5%5D%5Bselected_position%5D=Assistant+Director+of+Events&%5Bnew_officers%5D%5B5%5D%5Bdiscord_id%5D=224380364624363522&%5Bnew_officers%5D%5B5%5D%5Bsfu_computing_id%5D=jya184&%5Bnew_officers%5D%5B5%5D%5Bre_use_start_date%5D=on&%5Bnew_officers%5D%5B6%5D%5Bselected_position%5D=Director+of+Communications&%5Bnew_officers%5D%5B6%5D%5Bdiscord_id%5D=384163838938841088&%5Bnew_officers%5D%5B6%5D%5Bsfu_computing_id%5D=jkl53&%5Bnew_officers%5D%5B6%5D%5Bre_use_start_date%5D=on&%5Bnew_officers%5D%5B7%5D%5Bselected_position%5D=Director+of+Archives&%5Bnew_officers%5D%5B7%5D%5Bdiscord_id%5D=294968839874150401&%5Bnew_officers%5D%5B7%5D%5Bsfu_computing_id%5D=dhz1&%5Bnew_officers%5D%5B7%5D%5Bre_use_start_date%5D=on&%5Bnew_officers%5D%5B8%5D%5Bselected_position%5D=Executive+at+Large+1&%5Bnew_officers%5D%5B8%5D%5Bdiscord_id%5D=639701580299632641&%5Bnew_officers%5D%5B8%5D%5Bsfu_computing_id%5D=yla686&%5Bnew_officers%5D%5B8%5D%5Bstart_date%5D=2022-02-15&%5Bnew_officers%5D%5B9%5D%5Bselected_position%5D=Executive+at+Large+2&%5Bnew_officers%5D%5B9%5D%5Bdiscord_id%5D=600098482627280896&%5Bnew_officers%5D%5B9%5D%5Bsfu_computing_id%5D=jnr2&%5Bnew_officers%5D%5B9%5D%5Bstart_date%5D=2022-02-15&%5Bnew_officers%5D%5B10%5D%5Bselected_position%5D=First+Year+Representative+1&%5Bnew_officers%5D%5B10%5D%5Bdiscord_id%5D=118521037154418694&%5Bnew_officers%5D%5B10%5D%5Bsfu_computing_id%5D=jmr26&%5Bnew_officers%5D%5B10%5D%5Bre_use_start_date%5D=on&%5Bnew_officers%5D%5B11%5D%5Bselected_position%5D=First+Year+Representative+2&%5Bnew_officers%5D%5B11%5D%5Bdiscord_id%5D=375806164103069700&%5Bnew_officers%5D%5B11%5D%5Bsfu_computing_id%5D=yjs2&%5Bnew_officers%5D%5B11%5D%5Bre_use_start_date%5D=on&%5Bnew_officers%5D%5B12%5D%5Bselected_position%5D=SFSS+Council+Representative&%5Bnew_officers%5D%5B12%5D%5Bdiscord_id%5D=124044674372599808&%5Bnew_officers%5D%5B12%5D%5Bsfu_computing_id%5D=trumanb&%5Bnew_officers%5D%5B12%5D%5Bre_use_start_date%5D=on&da_name=Create+New+Officer+Links")
    if 'new_officers' in new_officers_dict and type(new_officers_dict['new_officers']) == dict:
        new_officers_dict['new_officers'] = list(new_officers_dict['new_officers'].values())
    fields = ['term', 'year', 'new_officers']
    error_message = verify_user_input_has_all_required_fields(new_officers_dict, fields=fields)
    if error_message != "":
        logger.info(
            f"[about/process_specified_new_officers.py process_specified_new_officers()] {error_message}"
        )
        create_context_for_specify_new_officers_html(
            context, error_messages=[error_message]
        )
        return render(request, 'about/input_new_officers/specify_new_officers.html', context)

    if not validate_user_command(new_officers_dict):
        error_message = "Unable to understand user command"
        logger.info(
            f"[about/process_specified_new_officers.py process_specified_new_officers()] {error_message}"
        )
        create_context_for_specify_new_officers_html(
            context, error_messages=[error_message],
            term=new_officers_dict['term'], year=new_officers_dict['year'],
            draft_new_officers=new_officers_dict['new_officers']
        )
        return render(request, 'about/input_new_officers/specify_new_officers.html', context)
    success, error_message = validate_inputted_term_info(new_officers_dict['term'], new_officers_dict['year'])
    if not success:
        logger.info(
            f"[about/process_specified_new_officers.py process_specified_new_officers()] {error_message}"
        )
        create_context_for_specify_new_officers_html(
            context, error_messages=[error_message],
            term=new_officers_dict['term'], year=new_officers_dict['year'],
            draft_new_officers=new_officers_dict['new_officers']
        )
        return render(request, 'about/input_new_officers/specify_new_officers.html', context)
    success, error_message = validate_inputted_new_officers(new_officers_dict['new_officers'])
    if not success:
        logger.info(
            f"[about/process_specified_new_officers.py process_specified_new_officers()] {error_message}"
        )
        create_context_for_specify_new_officers_html(
            context, error_messages=[error_message],
            term=new_officers_dict['term'], year=new_officers_dict['year'],
            draft_new_officers=new_officers_dict['new_officers']
        )
        return render(request, 'about/input_new_officers/specify_new_officers.html', context)
    # save_new_officers(new_officers_dict)
    return HttpResponseRedirect(f'{URL_ROOT}about/specify_new_officers')
