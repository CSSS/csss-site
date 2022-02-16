from about.models import OfficerEmailListAndPositionMapping, Officer
from csss.views_helper import get_current_term_number, get_previous_term


def determine_start_date(start_date, sfu_computing_id, position_name):
    position_obj = OfficerEmailListAndPositionMapping.objects.all().filter(position_name=position_name).first()
    if position_obj is None:
        return start_date
    if position_obj.number_of_terms == 1:
        return start_date
    if position_obj.starting_month is None:  # for position like By-Election Officer which have no real start-month
        return start_date
    current_term_number = get_current_term_number()
    if position_obj.starting_month == current_term_number:
        return start_date

    officer = Officer.objects.all().filter(
        sfuid=sfu_computing_id, position_name=position_name, start_date__gte=(get_previous_term() % 10)
    ).order_by('-start_date').first()
    if officer is None:
        return start_date
    if position_obj.number_of_terms is None:  # for positions that are never ending like Sys Admin
        return officer.start_date
    """
    position_obj        current_term_number         use_previous_start_date(2 terms)
    1                   1                           no (0)
    1                   2                           yes (-1)
    1                   3                           no (-2)
    2                   1                           no (1)
    2                   2                           no (0)
    2                   3                           yes (-1)
    3                   1                           yes (2)
    3                   2                           no (1)
    3                   3                           no (0)

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
    if (
            (position_obj.starting_month - current_term_number) == -1 or
            (position_obj.starting_month - current_term_number) == 2
    ):
        return officer.start_date

    return start_date
