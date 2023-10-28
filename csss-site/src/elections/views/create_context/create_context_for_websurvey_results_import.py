from csss.views.context_creation.create_authenticated_contexts import create_context_for_election_officer


def create_context_for_websurvey_results_import(request, tab=None):
    context = create_context_for_election_officer(request, tab=tab)
    return context
