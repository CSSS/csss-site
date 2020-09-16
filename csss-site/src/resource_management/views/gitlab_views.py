import logging

from about.models import Term, Officer
from csss.views_helper import get_current_active_term
from resource_management.models import NaughtyOfficer

logger = logging.getLogger('csss_site')


def create_gitlab_perms():
    """creates a list of all the user who will have gitlab access

    Return

    officer -- Example < sfuid1, sfuid2, sfuid3, sfuid3 >
    """
    term_active = get_current_active_term()
    officers = []

    for index in range(0, 5):
        term = Term.objects.get(term_number=term_active)
        logger.info(
            "[resource_management create_gitlab_perms()] collecting the list of officers "
            f"for the term with term_number {term_active}"
        )
        naughty_officers = NaughtyOfficer.objects.all()
        term_specific_officers = [
            officer for officer in Officer.objects.all().filter(elected_term=term)
            if officer.name not in [name.strip() for name in naughty_officers.name]
        ]

        logger.info(f"officers retrieved = {term_specific_officers}")
        if (term_active % 10) == 3:
            term_active -= 1
        elif (term_active % 10) == 2:
            term_active -= 1
        elif (term_active % 10) == 1:
            term_active -= 8
        officers.extend(term_specific_officers)
    officer = [officer.sfuid for officer in officers]
    return officer
