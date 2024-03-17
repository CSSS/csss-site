import csv
import json

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render

from csss.setup_logger import Loggers
from csss.views.context_creation.create_authenticated_contexts import create_context_for_election_officer
from elections.models import Election, VoterChoice
from elections.views.Constants import TAB_STRING, NO_CONFIDENCE_NAME, SKIPPED_VOTE, \
    URL_MAP_WEBSURVEY_NOMINEE_RESULTS, URL_MAP_WEBSURVEY_POSITION_RESULTS
from elections.views.create_context.import_websurvey_results.create_context_for_websurvey_results_html import \
    create_context_for_websurvey_results_html
from elections.views.import_websurvey_results.convert_pending_voter_choice_to_final import \
    convert_pending_voter_choice_to_final
from elections.views.import_websurvey_results.create_websurvey_column_position_mappings import \
    create_websurvey_column_position_mappings
from elections.views.import_websurvey_results.save_websurvey_nominees import save_websurvey_nominees
from elections.views.import_websurvey_results.send_notification_for_saved_election_results import \
    send_notification_for_saved_election_results


def import_websurvey_results(request, slug):
    """
    Shows the page where the election officer can upload the exported data from websurvey
    """
    logger = Loggers.get_logger()
    context = create_context_for_election_officer(request, tab=TAB_STRING)
    logger.info("[elections/import_websurvey_results.py import_websurvey_results()] request.POST=")
    logger.info(json.dumps(request.POST, indent=3))
    election_obj = Election.objects.get(slug=slug)
    if request.method == 'GET':
        create_context_for_websurvey_results_html(context, election_obj, import_websurvey_data=True)
        return render(request, 'elections/websurvey_results.html', context)
    else:
        uploaded_file = request.FILES['election_results']
        fs = FileSystemStorage()
        file_name = fs.save(uploaded_file.name, uploaded_file)

        # remove all existing result tracking objects as a fresh load of data is about to be imported to the site
        VoterChoice.objects.all().filter(selection__nominee_speech__nominee__election_id=election_obj.id).delete()
        election_obj.websurveycolumnpositionmapping_set.all().delete()
        election_obj.pendingvoterchoice_set.all().delete()

        with open(fs.path(file_name)) as csv_file:
            is_csv = '.csv' in file_name
            csv_reader = csv.reader(csv_file, delimiter=",") if is_csv else csv.reader(csv_file, delimiter='\t')
            rows = [row for row in csv_reader]
            nominee_names = [SKIPPED_VOTE, NO_CONFIDENCE_NAME]
            nominee_names.extend(list(set(election_obj.nominee_set.all().values_list('full_name', flat=True))))
            for row in rows[1:]:
                for index, nominee_name in enumerate(row[1:-1]):
                    save_websurvey_nominees(index, election_obj, nominee_name, nominee_names)

        # first attempts to convert as many pending voter choices to finalized to see if manual mapping is even
        # needed
        create_websurvey_column_position_mappings(election_obj)
        convert_pending_voter_choice_to_final(election_obj)
        # not doing anything with the success indicator returned from convert_pending_voter_choice_to_final as the
        # user has not yet had a chance to do manual mappings via the URL_MAP_WEBSURVEY_NOMINEE_RESULTS page

        # if create_websurvey_column_position_mappings and convert_pending_voter_choice_to_final
        # were able to map all the pending votes to finalized votes between them without any manual mapping
        # from the user
        pending_voter_choice = Election.objects.get(slug=slug).pendingvoterchoice_set.all()
        if pending_voter_choice.filter(nominee_name_mapped=False).count() > 0:
            redirect_page = f"{settings.URL_ROOT}elections/{slug}/{URL_MAP_WEBSURVEY_NOMINEE_RESULTS}/"
        elif pending_voter_choice.count() > 0:
            redirect_page = f"{settings.URL_ROOT}elections/{slug}/{URL_MAP_WEBSURVEY_POSITION_RESULTS}/"
        else:
            send_notification_for_saved_election_results(election_obj)
            redirect_page = f"{settings.URL_ROOT}elections/{slug}/"
        return HttpResponseRedirect(redirect_page)
