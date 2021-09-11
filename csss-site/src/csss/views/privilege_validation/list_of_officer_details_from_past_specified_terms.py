import logging

from about.models import Officer, Term
from csss.views_helper import get_current_term
from resource_management.models import NaughtyOfficer

logger = logging.getLogger('csss_site')


def get_list_of_officer_details_from_past_specified_terms(
        relevant_previous_terms=5, position_names=None, filter_by_github=False, filter_by_sfuid=False,
        naughty_officers=None, all_officers_in_relevant_terms=None
):
    """
    Returns the list of users who match the specified position_names and relevant_previous_terms

    Keyword Argument
    relevant_previous_terms - if 0 specified, only get current term
     if 1 is specified get current and previous term and so forth
    position_names -- indicates which officers to narrow the list down to if specified
    filter_by_github -- creates a list of just the relevant github usernames if set to True

    Return
    list of
     if filter_by_github == True:
      list of relevant github usernames
     else:
      list of relevant officer objects
    """
    logger.info(
        f"[resource_management/get_officer_list.py get_list_of_officer_details_from_past_specified_terms()]"
        f" called with relevant_previous_terms: {relevant_previous_terms}, position_names: {position_names},"
        f" filter_by_github: {filter_by_github}, filter_by_sfuid: {filter_by_sfuid}"
    )
    if naughty_officers is None:
        naughty_officers = [naughty_officer.sfuid.strip() for naughty_officer in NaughtyOfficer.objects.all()]
    if all_officers_in_relevant_terms is None:
        all_officers_in_relevant_terms = Officer.objects.all().filter(
            elected_term__in=Term.objects.all().filter(term_number__in=get_relevant_terms(relevant_previous_terms))
        )
    return [
        _extract_specified_info(officer, filter_by_github, filter_by_sfuid)
        for officer in all_officers_in_relevant_terms
        if _validate__officer(officer, position_names, naughty_officers)
    ]


def _validate__officer(officer, position_names, naughty_officers):
    return (officer.sfuid not in naughty_officers) and \
           ((position_names is not None and officer.position_name in position_names) or position_names is None)


def _extract_specified_info(officer, filter_by_github, filter_by_sfuid):
    if filter_by_github:
        return officer.github_username
    elif filter_by_sfuid:
        return officer.sfuid
    else:
        return officer


def get_relevant_terms(relevant_previous_terms=5):
    relevant_previous_terms += 1
    term_active = get_current_term()
    active_terms = []
    for index in range(0, relevant_previous_terms):
        active_terms.append(term_active)
        if (term_active % 10) == 3:
            term_active -= 1
        elif (term_active % 10) == 2:
            term_active -= 1
        elif (term_active % 10) == 1:
            term_active -= 8
    return active_terms
