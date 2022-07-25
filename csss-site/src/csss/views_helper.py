import datetime
import logging

from about.models import Term

logger = logging.getLogger('csss_site')

SPRING_TERM_NUMBER = 1
SUMMER_TERM_NUMBER = 2
FALL_TERM_NUMBER = 3
TERM_SEASONS = [term_choice[0] for term_choice in Term.term_choices]


def there_are_multiple_entries(post_dict, key_to_read):
    """
    Check to see if the given dictionary has an array or a single element at the specified key

    Keyword Argument
    post_dict -- the dictionary to check
    key_to_read -- the key in the dictionary to check

    return:
    True if the key contains an erray of elements rather than just 1 element. or None if that
     key is not in the dictionary
    """
    if key_to_read not in post_dict:
        return None
    return isinstance(post_dict[key_to_read], list)


def get_current_term():
    """
    Get the term number for the current term

    Return
    the term_number that fits the convention YYYY<1/2/3>
    """
    current_date = datetime.datetime.now()
    return get_term_number_for_specified_year_and_month(current_date.month, current_date.year)


def get_latest_term():
    """
    Get the term number for the latest term

    Return
    the term_number that fits the convention YYYY<1/2/3>
    """
    date_for_next_month = datetime.datetime.now()
    term_number_for_current_term = get_term_number_for_specified_year_and_month(
        date_for_next_month.month, date_for_next_month.year
    )
    term_number_for_next_term = get_term_number_for_specified_year_and_month(
        date_for_next_month.month, date_for_next_month.year
    )
    while term_number_for_current_term == term_number_for_next_term:
        date_for_next_month = date_for_next_month + datetime.timedelta(days=30)
        term_number_for_next_term = get_term_number_for_specified_year_and_month(
            date_for_next_month.month, date_for_next_month.year
        )


def get_last_summer_term():
    """
    Get the datetime that corresponds to the last relevant summer term

    Return
    -   if current_term is Spring
            returns the datetime for first day of Summer Term last year
        if current_term is Summer or Fall
            returns the datetime for the first day of Summer or Fall term of this year
    """
    current_date = datetime.datetime.now()
    if get_current_term_number() == SPRING_TERM_NUMBER:
        return get_datetime_for_beginning_of_specified_term(
            current_date.year - 1, 5, current_date.day
        )
    return get_datetime_for_beginning_of_specified_term(
        current_date.year, 5, current_date.day
    )


def get_last_fall_term():
    """
    Get the datetime that corresponds to the last relevant Fall term

    Return
    -   if current_term is Spring or Summer
            returns the datetime for first day of Fall Term last year
        if current_term is Fall
            returns the datetime for the first day of Fall term of this year
    """
    current_date = datetime.datetime.now()
    if get_current_term_number() in [SPRING_TERM_NUMBER, SUMMER_TERM_NUMBER]:
        return get_datetime_for_beginning_of_specified_term(
            current_date.year - 1, 9, current_date.day
        )
    return get_datetime_for_beginning_of_specified_term(
        current_date.year, 9, current_date.day
    )


def get_last_spring_term():
    """
    Get the datetime that corresponds to the last relevant Spring term

    Return
    -   if current_term is Spring or Summer or Fall
            returns the datetime for first day of Spring term of this year
    """
    current_date = datetime.datetime.now()
    return get_datetime_for_beginning_of_specified_term(
        current_date.year, current_date.month, current_date.day
    )


def get_current_term_number():
    """
    Get the term number for the current term

    Return
    the term_number that is either <1/2/3>
    """
    return get_current_term() % 10


def get_datetime_for_beginning_of_specified_term(year, month, day):
    """
    Gets the datetime for the beginning of the current term

    Return the datetime for the beginning of the current time where the month is Jan, May, Sept and the day is 1
    """
    current_date = datetime.datetime(year, month=month, day=day)
    while not date_is_first_day_of_term(current_date):
        current_date = current_date - datetime.timedelta(days=1)
    return current_date


def get_previous_term():
    current_date = datetime.datetime.now()
    return get_term_number_for_specified_year_and_month(current_date.month - 4, current_date.year)


def get_current_term_obj():
    """
    Get the term object that corresponds to current term

    Return
    term -- either the term object if it exists or None
    """
    terms = Term.objects.all().filter(term_number=get_current_term())
    return None if len(terms) == 0 else terms[0]


def get_term_number_for_specified_year_and_month(month, year):
    """
    get the term_number for the term that maps to the specified month and year

    keyword argument
    month -- the month's number (1-12)
    year -- the year's number

    return: the term_number that fits the convention YYY<1/2/3>
    """
    term_active = (year * 10)
    if int(month) <= 4:
        term_active += 1
    elif int(month) <= 8:
        term_active += 2
    else:
        term_active += 3
    return term_active


def get_datetime_for_beginning_of_current_term():
    """
    Gets the datetime for the beginning of the current term

    Return the datetime for the beginning of the current time where the month is Jan, May, Sept and the day is 1
    """
    current_date = datetime.datetime.now()
    while not date_is_first_day_of_term(current_date):
        current_date = current_date - datetime.timedelta(days=1)
    return current_date


def date_is_first_day_of_term(current_date):
    """
    Returns a bool to indicate if given date is the first date of a School Term

    Keyword Argument
    current_date -- the date to check

    Return
    bool
    """
    return (current_date.month == 1 or current_date.month == 5 or current_date.month == 9) and current_date.day == 1


def determine_if_specified_term_obj_is_for_current_term(term_obj):
    """
    Returns a bool that indicates if the specified term obj points to the current term

    Keyword Argument
    term_obj -- the specified term obj

    Return
    Bool -- true if the term obj points to the current term, otherwise False
    """
    current_date = datetime.datetime.now()
    if int(current_date.month) <= 4:
        term_season_index = 0
    elif int(current_date.month) <= 8:
        term_season_index = 1
    else:
        term_season_index = 2
    current_season = TERM_SEASONS[term_season_index]
    return term_obj.year == current_date.year and term_obj.term == current_season
