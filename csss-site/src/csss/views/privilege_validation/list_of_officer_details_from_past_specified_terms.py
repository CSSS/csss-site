import logging

from about.models import Officer, Term, UnProcessedOfficer
from csss.views_helper import get_current_term

logger = logging.getLogger('csss_site')


def get_list_of_officer_details_from_past_specified_terms(
        relevant_previous_terms=5, position_names=None, filter_by_github=False, filter_by_sfuid=False,
        unprocessed_officers=None, all_officers_in_relevant_terms=None, current_officer_only=False
):
    """
    Returns the list of users who match the specified position_names and relevant_previous_terms

    Keyword Argument
    relevant_previous_terms - if 0 specified, only get current term
     if 1 is specified get current and previous term and so forth
    position_names -- indicates which officers to narrow the list down to if specified
    filter_by_github -- creates a list of just the relevant github usernames if set to True
    filter_by_sfuid -- creates a list of just the relevant SFUIDs if set to True
    unprocessed_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    all_officers_in_relevant_terms -- the list of officers for the relevant terms that need to be filtered down
    current_officer_only -- flag to indicate if just 1 entry needs to be returned or a list of officers

    Return
    if current_officer_only
        the most recent officer's bio, github username or SFUID who matches the specified conditions
    else
        list of recent officer's bio, github usernames or SFUIDS that match the specified condition
    """
    logger.info(
        f"[resource_management/get_officer_list.py get_list_of_officer_details_from_past_specified_terms()]"
        f" called with relevant_previous_terms: {relevant_previous_terms}, position_names: {position_names},"
        f" filter_by_github: {filter_by_github}, filter_by_sfuid: {filter_by_sfuid}"
    )
    if unprocessed_officers is None:
        unprocessed_officers = [
            unprocessed_officer.sfu_computing_id.strip() for unprocessed_officer in UnProcessedOfficer.objects.all()
        ]
    if all_officers_in_relevant_terms is None:
        all_officers_in_relevant_terms = Officer.objects.all().filter(
            elected_term__in=Term.objects.all().filter(
                term_number__in=get_relevant_terms(relevant_previous_terms)
            )
        ).order_by('-start_date')
    officer_in_specified_terms_with_specified_position_names = [
        _extract_specified_info(officer, filter_by_github, filter_by_sfuid)
        for officer in all_officers_in_relevant_terms
        if _validate__officer(officer, position_names, unprocessed_officers)
    ]
    if current_officer_only:
        return None if len(officer_in_specified_terms_with_specified_position_names) == 0 \
            else officer_in_specified_terms_with_specified_position_names[0]
    else:
        return officer_in_specified_terms_with_specified_position_names


def _validate__officer(officer, position_names, unprocessed_officers):
    """
    Returns true if the officer has updated their bio and their position names fit under the
    position names list contraint

    Keyword Argument
    officer -- the officer who has to be checked
    position_names -- the list of positions that the officers are needed for
    unprocessed_officers -- the list of SFUIDs for officer who have not yet added their latest bio

    Return
    Bool -- True if the officer validates the contraints
    """
    return (officer.sfu_computing_id not in unprocessed_officers) and \
           ((position_names is not None and officer.position_name in position_names) or position_names is None)


def _extract_specified_info(officer, filter_by_github, filter_by_sfuid):
    """
    Returns either the officer bio, github username or SFUID depending on the specified filters

    Keyword Argument
    officer -- the officer object whose profile has to be returned
    filter_by_github -- indicate whether or not to return just the officer's github username
    filter_by_sfuid -- indicates whether or not to return just the officer's SFUID

    Return
    the officer's bio, github username or SFUID
    """
    if filter_by_github:
        return officer.github_username
    elif filter_by_sfuid:
        return officer.sfu_computing_id
    else:
        return officer


def get_relevant_terms(relevant_previous_terms=5):
    """
    Get a list of the term_number relevant to the terms that fit in the parameter

    Keyword Argument
    relevant_previous_terms - if 0 specified, only get current term
     if 1 is specified get current and previous term and so forth

    Return
    list of the terms_numbers that fit under the specified relevant_previous_terms
    """
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
