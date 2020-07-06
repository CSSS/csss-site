import datetime
import logging

from about.models import Term, Officer
from resource_management.models import NaughtyOfficer

logger = logging.getLogger('csss_site')


def create_gitlab_perms():
    """creates a list of all the user who will have gitlab access

    Return

    officer -- Example < sfuid1, sfuid2, sfuid3, sfuid3 >
    """
    current_date = datetime.datetime.now()
    term_active = (current_date.year * 10)
    if int(current_date.month) <= 4:
        term_active += 1
    elif int(current_date.month) <= 8:
        term_active += 2
    else:
        term_active += 3
    officers = []

    for index in range(0, 5):
        term = Term.objects.get(term_number=term_active)
        logger.info(f"[resource_management create_gitlab_perms()] collecting the list of officers for the term with term_number {term_active}")
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
