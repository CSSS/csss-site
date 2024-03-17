import json

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.setup_logger import Loggers
from csss.views.context_creation.create_authenticated_contexts import create_context_for_election_officer
from elections.models import Election, VoterChoice, PendingVoterChoice, \
    WebsurveyColumnPositionMapping
from elections.views.Constants import TAB_STRING, URL_IMPORT_WEBSURVEY_RESULTS, URL_MAP_WEBSURVEY_NOMINEE_RESULTS, \
    RESULT_POSITIONS_KEY, NA_STRING, RE_IMPORT_WEBSURVEY_ELECTION_KEY
from elections.views.create_context.import_websurvey_results.create_context_for_websurvey_results_html import \
    create_context_for_websurvey_results_html
from elections.views.import_websurvey_results.convert_pending_voter_choice_to_final import \
    convert_pending_voter_choice_to_final
from elections.views.import_websurvey_results.get_dict_for_election_position_name_mapping import \
    get_dict_for_election_position_name_mapping
from elections.views.import_websurvey_results.send_notification_for_saved_election_results import \
    send_notification_for_saved_election_results
from elections.views.utils.webform_to_json.transform_post_to_dictionary import transform_post_to_dictionary


def map_websurvey_position_results(request, slug):
    """
    Shows the page where the election officer can map a websurvey column in the websurvey results to one of the
     positions that were voted for in the election
    """
    logger = Loggers.get_logger()
    context = create_context_for_election_officer(request, tab=TAB_STRING)
    logger.info("[elections/map_websurvey_position_results.py map_websurvey_position_results()] request.POST=")
    logger.info(json.dumps(request.POST, indent=3))
    election_obj = Election.objects.get(slug=slug)
    pending_voter_choices = election_obj.pendingvoterchoice_set.all()
    if request.method == 'POST' and RE_IMPORT_WEBSURVEY_ELECTION_KEY in request.POST:
        PendingVoterChoice.objects.all().filter(election=election_obj).delete()
        VoterChoice.objects.all().filter(selection__nominee_speech__nominee__election_id=election_obj.id).delete()
        WebsurveyColumnPositionMapping.objects.all().filter(election_id=election_obj.id).delete()
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/{slug}/{URL_IMPORT_WEBSURVEY_RESULTS}/")
    if pending_voter_choices.count() == 0:
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/{slug}/{URL_IMPORT_WEBSURVEY_RESULTS}/")
    if pending_voter_choices.filter(nominee_name_mapped=False).count() > 0:
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/{slug}/{URL_MAP_WEBSURVEY_NOMINEE_RESULTS}/")
    if request.method == 'GET':
        election_position_name_mapping = get_dict_for_election_position_name_mapping(
            election_obj, pending_voter_choices
        )
        if len(election_position_name_mapping) == 0:
            return HttpResponseRedirect(f"{settings.URL_ROOT}elections/{slug}/")
        create_context_for_websurvey_results_html(context, election_obj, map_websurvey_positions=True,
                                                  election_position_name_mappings=election_position_name_mapping)
        return render(request, 'elections/websurvey_results.html', context)
    else:
        post_dict = transform_post_to_dictionary(request)
        errors = []

        for question_number, mapped_position_name in post_dict[RESULT_POSITIONS_KEY].items():
            if mapped_position_name == NA_STRING:
                errors.append(f"Did not detect a selection for WebSurvey Question {question_number}")

        post_dict[RESULT_POSITIONS_KEY] = {
            question_number-1: mapped_position_name
            for question_number, mapped_position_name in post_dict[RESULT_POSITIONS_KEY].items()
        }

        if len(errors) > 0:
            create_context_for_websurvey_results_html(
                context, election_obj, map_websurvey_positions=True,
                errors=errors, pending_voter_choices=pending_voter_choices,
                selected_position_mappings=post_dict[RESULT_POSITIONS_KEY]
            )
            return render(request, 'elections/websurvey_results.html', context)
        for websurvey_column, relevant_position_name in post_dict[RESULT_POSITIONS_KEY].items():
            WebsurveyColumnPositionMapping(
                websurvey_column=websurvey_column, election=election_obj,
                position_name=relevant_position_name
            ).save()
        success, problematic_pending_voter_choice_id = convert_pending_voter_choice_to_final(election_obj)
        if not success:
            pending_voter_choice = PendingVoterChoice.objects.all().get(id=problematic_pending_voter_choice_id)
            create_context_for_websurvey_results_html(
                context, election_obj, map_websurvey_positions=True,
                errors=[f"Unable to Finalize Voter Choice with name {pending_voter_choice.full_name}"],
                pending_voter_choices=pending_voter_choices,
                selected_position_mappings=post_dict[RESULT_POSITIONS_KEY]
            )
            return render(request, 'elections/websurvey_results.html', context)
        send_notification_for_saved_election_results(election_obj)
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/{slug}/")
