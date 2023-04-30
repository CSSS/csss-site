import datetime

from csss.setup_logger import Loggers
from csss.views.time_converter import create_pst_time_from_datetime
from csss.views_helper import get_current_term_obj

"""
Determine Start Date Logic
starting_month -> May
President [3 terms]
V-P [3 terms]
Treasurer [3 terms]
Director of Resources [3 terms]
Director of Events [3 terms]
Assistant Director of Events [3 terms]
Director of Communications [3 terms]
Director of Archives [3 terms]
SFSS Council Rep [3 terms]

Starting Month -> January, May, September
Exec at large 1 [1 term]
Exec at large 2 [1 term]

Starting_month -> September
First Year Rep 1 [2 terms]
First year Rep 2 [2 terms]

starting_month -> Spring
General Election Officer [1 term]
    never carry a start date
Frosh Week Chair [2-3 terms, 3 if elected in Spring, 2 if elected in Summer]

starting_month -> None
By-Election Officer [1 term]

never-ending
Systems Administrator
webmaster
"""


def determine_start_date(
        officers, officer_email_list_and_position_mapping, re_use_start_date, start_date, sfu_computing_id,
        position_name, target_term):
    """
    Determines the start date to use for a New_Officer

    Keyword Arguments
    officers -- the list of all the officers ever
    officer_email_list_and_position_mapping -- the list of officer, email list and position mapping
    re_use_start_date -- whether the user indicated they want re-use the start date from a previous term
    start_date -- the start date that the user has entered for the New_Officer
    sfu_computing_id -- the sfu computing ID of the New_Officer
    position_name -- the name of the position that the New_Officer has been elected to
    target_term -- the term that the new officer will be saved under

    Return
    start_date -- the start date to use for the UnProcessed Officer
    """
    logger = Loggers.get_logger()
    if not re_use_start_date:
        return create_pst_time_from_datetime
    position_obj = officer_email_list_and_position_mapping.filter(position_name=position_name).first()
    if position_obj.number_of_terms == 1:
        logger.info(
            f"[about/determine_start_date.py determine_start_date()] using the new start_date of {start_date} "
            f"since the number of terms for the position {position_name} is 1"
        )
        return start_date
    if position_obj.get_term_month_number() is None and position_obj.number_of_terms is not None:
        # for position like By-Election Officer which have no real start-month and may sometimes cover 1 or 2 terms,
        # depending on when they are elected. Like if they are elected at the very end of a term
        logger.info(
            f"[about/determine_start_date.py determine_start_date()] no starting month detected for position "
            f"{position_name}, will revert to using start_date {start_date}"
        )
        return start_date
    logger.info(
        f"[about/determine_start_date.py determine_start_date()] target_term.get_term_month_number()="
        f"{target_term.get_term_month_number()} "
    )
    if position_obj.get_term_month_number() == target_term.get_term_month_number():
        logger.info(
            f"[about/determine_start_date.py determine_start_date()] the current term is the term that the position"
            f" {position_name} starts in....will revert to using the new start_date of {start_date} as a result"
        )
        return start_date
    officer = officers.filter(
        sfu_computing_id=sfu_computing_id, position_name=position_name, elected_term=get_current_term_obj()
    ).order_by('-id').first()
    if officer is None:
        logger.info(
            f"[about/determine_start_date.py determine_start_date()] the officer with sfu_computing_id "
            f"{sfu_computing_id} did not hold the position of {position_name} on any date after "
            f"{get_current_term_obj()}. Reverting to start_date {start_date}"
        )
        return start_date
    if position_obj.number_of_terms is None:  # for positions that are never ending like Sys Admin
        logger.info(
            f"[about/determine_start_date.py determine_start_date()] the officer with sfu_computing_id "
            f"{sfu_computing_id} is holding a position that has no end-date [{position_name}]. "
            f"Will use their current start_date of {officer.start_date}"
        )
        return officer.start_date
    if position_obj.number_of_terms == 3:
        # will have to rely on users to know not to select "Officer did not have to be voted into position again this
        # term:" for people in a year-long term
        return officer.start_date
    if (
        position_obj.number_of_terms == 2 and
        (
            target_term.get_term_month_number() - position_obj.get_term_month_number() == 1 or
            target_term.get_term_month_number() - position_obj.get_term_month_number() == -2
        )
    ):
        """
        target_term_number
        1
            shares starting_date: 2             [2-1] = 1
            does not share starting_date: 1, 3  [1-1] = 0 && [3-1] = 2
        2
            shares starting date: 3             [3-2] == 1
            does not share starting_date: 1, 2  [1-2] == -1 && [2-2] = 0
        3
            shares starting date: 1             [1-3] = -2
            does not share starting_date: 2, 3  [2-3] = -1 && [3-3] = 0
        """
        logger.info(
            "[about/determine_start_date.py determine_start_date()]  using the officer's current start_date "
            f"{officer.start_date}"
            " since it seems they were holding this position last month and its not a cut-off time yet"
            "\n(position_obj.starting_month - target_term.get_term_month_number()) ="
            f"{(position_obj.get_term_month_number() - target_term.get_term_month_number())}"
            "\n(position_obj.starting_month - target_term.get_term_month_number())="
            f"{(position_obj.get_term_month_number() - target_term.get_term_month_number())}"
        )
        start_date = officer.start_date
    else:
        logger.info(
            f"[about/determine_start_date.py determine_start_date()]  reverting to using the new start_date of "
            f"{start_date} after all"
        )
    return start_date
