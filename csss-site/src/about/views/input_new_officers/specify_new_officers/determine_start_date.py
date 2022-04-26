import logging

from about.models import OfficerEmailListAndPositionMapping, Officer
from csss.views_helper import get_current_term_number, get_current_term_obj

logger = logging.getLogger('csss_site')


def determine_start_date(re_use_start_date, start_date, sfu_computing_id, position_name):
    """
    starting_month -> May
    how_many_terms 3
    President
    V-P
    Treasurer
    Director of Resources
    Director of Events
    Assistant Director of Events
    Director of Communications
    Director of Archives
    SFSS Council Rep

    Starting Month -> January, May, September
    how many terms -> 1
    Exec at large 1
    Exec at large 2

    Starting_month -> September
    how many terms -> 2
    First Year Rep 1
    First year Rep 2

    starting_month -> Spring
    how many terms -> 2
    General Election Officer

    never carry a start date
    starting_month -> None
    By-Election Officer

    year_long starting in Spring
    Frosh Week Chair

    never-ending
    Systems Administrator
    webmaster
    """
    if not re_use_start_date:
        return start_date
    position_obj = OfficerEmailListAndPositionMapping.objects.all().filter(position_name=position_name).first()
    if position_obj.number_of_terms == 1:
        logger.info(
            f"[about/determine_start_date.py determine_start_date()] using the new start_date of {start_date} "
            f"since the number of terms for the position {position_name} is 1"
        )
        return start_date
    if position_obj.starting_month is None and position_obj.number_of_terms is not None:
        # for position like By-Election Officer which have no real start-month and don't run on forever
        logger.info(
            f"[about/determine_start_date.py determine_start_date()] no starting month detected for position "
            f"{position_name}, will revert to using start_date {start_date}"
        )
        return start_date
    current_term_number = get_current_term_number()
    logger.info(
        f"[about/determine_start_date.py determine_start_date()] current_term_number={current_term_number} "
    )
    if position_obj.starting_month == current_term_number:
        logger.info(
            f"[about/determine_start_date.py determine_start_date()] no starting month detected for position "
            f"{position_name}, will revert to using start_date {start_date}"
        )
        return start_date
    officer = Officer.objects.all().filter(
        sfuid=sfu_computing_id, position_name=position_name, elected_term=get_current_term_obj()
    ).order_by('-elected_term').first()
    if officer is None:
        logger.info(
            f"[about/determine_start_date.py determine_start_date()] the officer with sfuid {sfu_computing_id} "
            f"did not hold the position of {position_name} on any date after {get_current_term_obj()}."
            f" Reverting to start_date {start_date}"
        )
        return start_date
    if position_obj.number_of_terms is None:  # for positions that are never ending like Sys Admin
        logger.info(
            f"[about/determine_start_date.py determine_start_date()] the officer with sfuid {sfu_computing_id} "
            f"is holding a position that has no end-date [{position_name}]. Will use their current start_date of"
            f" {officer.start_date}"
        )
        return officer.start_date
    if position_obj.number_of_terms == 3:
        # will have to rely on users to know not to select "Officer did not have to be voted into position again this
        # term:" for people in a year-long term
        return officer.start_date
    if (
            position_obj.number_of_terms == 2 and
            (
                    current_term_number - position_obj.starting_month == 0 or
                    current_term_number - position_obj.starting_month == -2 or
                    current_term_number - position_obj.starting_month == 1
            )
    ):
        """
        current_term_number     position_obj.starting_month = 
        1                       1                           yes     [0]
        1                       2                           no  [-1]
        1                       3                           yes     [-2]
        2                       1                           yes     [1]
        2                       2                           yes     [0]
        2                       3                           no  [-1]
        3                       1                           no  [2]
        3                       2                           yes     [1]
        3                       3                           yes     [0]
        
        """
        logger.info(
            f"[about/determine_start_date.py determine_start_date()]  using the officer's current start_date {officer.start_date}"
            f" since it seems they were holding this position last month and its not a cut-off time yet"
            f"\n(position_obj.starting_month - current_term_number) ={(position_obj.starting_month - current_term_number)}"
            f"\n(position_obj.starting_month - current_term_number)={(position_obj.starting_month - current_term_number)}"
        )
    logger.info(
        f"[about/determine_start_date.py determine_start_date()]  reverting to using the new start_date of {start_date}"
        f" after all"
    )
    return start_date
