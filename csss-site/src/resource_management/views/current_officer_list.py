import logging

from about.models import Term, Officer
from csss.views_helper import get_current_active_term
from resource_management.models import NaughtyOfficer

logger = logging.getLogger('csss_site')


def create_current_officer_list():
    """
    Returns the list of users who currently need to have access to the SFU CSSS Digital Resources
    """
    term_active = get_current_active_term()
    officer_list = []
    for index in range(0, 5):
        term = Term.objects.get(term_number=term_active)
        logger.info(
            f"[resource_management/current_officer_list.py create_current_officer_list()] collecting the "
            f"list of officers for the term with term_number {term_active}"
        )
        naughty_officers = [naughty_officer.name.strip() for naughty_officer in NaughtyOfficer.objects.all()]
        current_officers = [
            officer for officer in Officer.objects.all().filter(elected_term=term)
            if len([
                naughty_officer for naughty_officer in naughty_officers if naughty_officer in officer.name
            ]) == 0
        ]

        logger.info(
            "[resource_management/current_officer_list.py create_current_officer_list()] current_officers retrieved"
            f" = {current_officers}"
        )
        officer_list.extend(current_officers)
        if (term_active % 10) == 3:
            term_active -= 1
        elif (term_active % 10) == 2:
            term_active -= 1
        elif (term_active % 10) == 1:
            term_active -= 8
    return officer_list
