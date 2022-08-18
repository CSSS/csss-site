from about.models import Term

FIRST_TERM_SEASON = Term.term_choices[0][0]
SECOND_TERM_SEASON = Term.term_choices[1][0]
THIRD_TERM_SEASON = Term.term_choices[2][0]
TERM_SEASON_NUMBERS = {
    FIRST_TERM_SEASON: 0,
    SECOND_TERM_SEASON: 1,
    THIRD_TERM_SEASON: 2
}


def get_term_season_number(term_season):
    """
    Gets the term number using the specified season

    Keyword Arguments
    term -- the term object that the function will return its number

    Returns
    term_season_number -- the number of the tem, e.g. 1, 2, or 3. this can also be None if the
        term does not have a valid season
    """
    return TERM_SEASON_NUMBERS[term_season] if term_season in TERM_SEASON_NUMBERS else None
