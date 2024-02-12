import json

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.setup_logger import Loggers
from csss.views.context_creation.create_authenticated_contexts import create_context_for_election_officer
from elections.models import Election, VoterChoice, PendingVoterChoice
from elections.views.Constants import TAB_STRING, URL_IMPORT_WEBSURVEY_RESULTS, \
    URL_MAP_WEBSURVEY_POSITION_RESULTS, RE_IMPORT_WEBSURVEY_ELECTION_KEY, NOMINEE_NAME_KEY, NA_STRING
from elections.views.create_context.import_websurvey_results.create_context_for_websurvey_results_html import \
    create_context_for_websurvey_results_html
from elections.views.import_websurvey_results.convert_pending_voter_choice_to_final import \
    convert_pending_voter_choice_to_final
from elections.views.import_websurvey_results.create_websurvey_column_position_mappings import \
    create_websurvey_column_position_mappings
from elections.views.utils.webform_to_json.transform_post_to_dictionary import transform_post_to_dictionary


def map_websurvey_nominee_results(request, slug):
    """
    Shows the page where the election officer can map a nominee in the websurvey results to the recorded nominees
     for an election
    """
    logger = Loggers.get_logger()
    context = create_context_for_election_officer(request, tab=TAB_STRING)
    logger.info("[elections/map_websurvey_nominee_results.py map_websurvey_nominee_results()] request.POST=")
    logger.info(json.dumps(request.POST, indent=3))
    election_obj = Election.objects.get(slug=slug)
    pending_voter_choices = election_obj.pendingvoterchoice_set.all()
    if request.method == 'POST' and RE_IMPORT_WEBSURVEY_ELECTION_KEY in request.POST:
        election_obj.websurveycolumnpositionmapping_set.all().delete()
        election_obj.pendingvoterchoice_set.all().delete()
        VoterChoice.objects.all().filter(selection__nominee_speech__nominee__election_id=election_obj.id).delete()
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/{slug}/{URL_IMPORT_WEBSURVEY_RESULTS}/")
    if pending_voter_choices.count() == 0:
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/{slug}/{URL_IMPORT_WEBSURVEY_RESULTS}/")
    if pending_voter_choices.filter(nominee_name_mapped=False).count() == 0:
        return HttpResponseRedirect(f"{settings.URL_ROOT}elections/{slug}/{URL_MAP_WEBSURVEY_POSITION_RESULTS}/")
    if request.method == 'GET':
        create_context_for_websurvey_results_html(
            context, election_obj, pending_voter_choices=pending_voter_choices,
            map_websurvey_nominees=True
        )
        return render(request, 'elections/websurvey_results.html', context)
    else:
        post_dict = transform_post_to_dictionary(request)
        errors = []
        for nominee_name_from_input_file, mapped_nominee_name in post_dict[NOMINEE_NAME_KEY].items():
            if mapped_nominee_name == NA_STRING:
                errors.append(f"Invalid Selection detected for '{nominee_name_from_input_file}'")

        if len(errors) > 0:
            create_context_for_websurvey_results_html(
                context, election_obj, pending_voter_choices=pending_voter_choices,
                errors=errors, map_websurvey_nominees=True
            )
            return render(request, 'elections/websurvey_results.html', context)
        for pending_voter_choice in election_obj.pendingvoterchoice_set.all().filter(nominee_name_mapped=False):
            nominee_obj = election_obj.nominee_set.all().filter(full_name=pending_voter_choice.full_name).first()
            if nominee_obj:
                name = nominee_obj.full_name
            else:
                name = post_dict[NOMINEE_NAME_KEY][pending_voter_choice.full_name]
            pending_voter_choice.full_name = name
            pending_voter_choice.nominee_name_mapped = True
            pending_voter_choice.save()
        create_websurvey_column_position_mappings(election_obj)
        success, problematic_pending_voter_choice_id = convert_pending_voter_choice_to_final(election_obj)
        if not success:
            pending_voter_choice = PendingVoterChoice.objects.all().get(id=problematic_pending_voter_choice_id)
            create_context_for_websurvey_results_html(
                context, election_obj, pending_voter_choices=pending_voter_choices,
                errors=[f"Unable to Finalize Voter Choice with name {pending_voter_choice.full_name}"],
                map_websurvey_nominees=True
            )
            return render(request, 'elections/websurvey_results.html', context)
        if Election.objects.get(slug=slug).pendingvoterchoice_set.all().count() == 0:
            redirect_page = f"{settings.URL_ROOT}elections/{slug}/"
        else:
            redirect_page = f"{settings.URL_ROOT}elections/{slug}/{URL_MAP_WEBSURVEY_POSITION_RESULTS}/"
        return HttpResponseRedirect(redirect_page)
