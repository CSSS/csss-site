import logging

from about.models import Term, Officer
from csss.views_helper import get_current_term
from resource_management.models import NaughtyOfficer

logger = logging.getLogger('csss_site')


def get_list_of_officer_details_from_past_specified_terms(
        relevant_previous_terms=5, position_names=None, filter_by_github=False):
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
    term_active = get_current_term()
    officer_list = []
    relevant_previous_terms += 1
    for index in range(0, relevant_previous_terms):
        term = Term.objects.get(term_number=term_active)
        logger.info(
            f"[resource_management/get_officer_list.py get_list_of_officer_details_from_past_specified_terms()]"
            f" collecting the list of officers for the term with term_number {term_active}"
        )
        naughty_officers = [naughty_officer.name.strip() for naughty_officer in NaughtyOfficer.objects.all()]
        current_officers = [
            officer for officer in Officer.objects.all().filter(elected_term=term)
            if len([
                naughty_officer for naughty_officer in naughty_officers if naughty_officer in officer.name
            ]) == 0 and ((position_names is not None and officer.position_name in position_names) or (
                        position_names is None))
        ]

        logger.info(
            "[resource_management/get_officer_list.py get_list_of_officer_details_from_past_specified_terms()]"
            f" current_officers retrieved = {current_officers}"
        )
        if filter_by_github:
            for current_officer in current_officers:
                if current_officer.github_username not in officer_list:
                    officer_list.append(current_officer.github_username)
        else:
            officer_list.extend(current_officers)
        if (term_active % 10) == 3:
            term_active -= 1
        elif (term_active % 10) == 2:
            term_active -= 1
        elif (term_active % 10) == 1:
            term_active -= 8
    return officer_list
