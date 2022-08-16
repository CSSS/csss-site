from about.views.Constants import ID_KEY, START_DATE_KEY, POSITION_NAME_KEY, FULL_NAME_KEY, DISCORD_ID_KEY, \
    SFU_COMPUTING_ID_KEY, RE_USE_START_DATE_KEY
from about.views.input_new_officers.specify_new_officers.validators.validate_discord_id import validate_discord_id
from about.views.input_new_officers.specify_new_officers.validators.validate_sfu_id import validate_sfu_id
from about.views.input_new_officers.specify_new_officers.validators.validate_start_date import validate_start_date


def validate_inputted_unprocessed_officers(
    saved_unprocessed_officers, officer_emaillist_and_position_mappings, officers, terms, inputted_term,
        inputted_year, unprocessed_officers=None):
    """
    validates the inputted unprocessed officers position_names, full_name, discord_id, sfu_computing_id, start_date
    and ensures that any officer is not being used for more than 1 executive officer in any given term

    Keyword Argument
    saved_unprocessed_officers -- the queryset of currently saved unprocessed officers
    officer_emaillist_and_position_mappings -- the queryset of currently saved position infos
    officers -- the queryset of currently saved officers
    terms -- the queryset of currently saved terms
    inputted_term -- the term that the unprocessed officers were voted in
    inputted_year -- the year that the unprocessed officers were voted in
    unprocessed_officers -- the unprocessed officers that the user has inputted

    Return
    bool -- indicator of whether the validation was successful
    error_message -- whatever error message there was as a result of the validation, or None
    """
    if unprocessed_officers is None:
        return True, None
    selected_positions = []
    discord_ids = []
    unprocessed_officers_sfu_computing_ids = []
    valid_ids = []

    # will create a map of the currently filled executive positions and who is filling those roles to
    # determine if anyone is being given 2+ executive roles in the same term
    term = terms.filter(term=inputted_term, year=inputted_year).first()
    currently_held_executive_positions = {}
    if term is not None:
        current_officers_in_selected_term = officers.filter(elected_term=term).order_by(START_DATE_KEY)
        for current_officer_in_selected_term in current_officers_in_selected_term:
            selected_position = officer_emaillist_and_position_mappings.filter(
                position_name=current_officer_in_selected_term.position_name
            ).first()
            if selected_position is not None and selected_position.executive_officer:
                currently_held_executive_positions[current_officer_in_selected_term.position_name] = \
                    current_officer_in_selected_term

    for unprocessed_officer in unprocessed_officers:
        if ID_KEY in unprocessed_officer:
            if saved_unprocessed_officers.filter(id=unprocessed_officer[ID_KEY]).first() is None:
                del unprocessed_officer[ID_KEY]
            elif unprocessed_officer[ID_KEY] in valid_ids:
                del unprocessed_officer[ID_KEY]
            else:
                valid_ids.append(unprocessed_officer[ID_KEY])
        selected_position_name = unprocessed_officer[POSITION_NAME_KEY].strip()
        if selected_position_name in selected_positions:
            return False, f"You cannot have more than 1 {selected_position_name}"
        selected_position = officer_emaillist_and_position_mappings.filter(
            position_name=selected_position_name
        ).first()
        if selected_position is None:
            return False, f"Invalid position of {selected_position} specified"
        officer_name = unprocessed_officer[FULL_NAME_KEY].strip()
        if ' ' not in officer_name:
            return False, f"Could not detect a full name for \"{officer_name}\" [first AND last name]"
        selected_positions.append(selected_position_name)
        if len(unprocessed_officer[DISCORD_ID_KEY].strip()) > 0:
            discord_id = unprocessed_officer[DISCORD_ID_KEY].strip()
            valid, error_message = validate_discord_id(discord_id)
            if not valid:
                return False, f"invalid error of {error_message} with Discord ID of {discord_id}"
            if discord_id in discord_ids:
                return False, f"the discord ID of {discord_id} was entered more than once"
            discord_ids.append(discord_id)
        sfu_computing_id = unprocessed_officer[SFU_COMPUTING_ID_KEY].strip()
        success, error_message = validate_sfu_id(sfu_computing_id)
        if not success:
            return False, error_message
        if selected_position.executive_officer:
            if sfu_computing_id in unprocessed_officers_sfu_computing_ids:
                return False, "Someone cannot hold 2+ executive position in a given term"
            unprocessed_officers_sfu_computing_ids.append(sfu_computing_id)
        if not (RE_USE_START_DATE_KEY in unprocessed_officer or START_DATE_KEY in unprocessed_officer):
            return False, "One of the position does not have a new date and is not re-using a previous date"
        start_date = unprocessed_officer[START_DATE_KEY].strip()
        success, error_message = validate_start_date(start_date)
        if not success:
            return success, error_message
        if selected_position_name in currently_held_executive_positions:
            del currently_held_executive_positions[selected_position.position_name]

    if term is not None:
        # list of all the executive officers that will retain their executive status even after all the unprocessed
        # officers are processed
        current_executive_officers_not_being_overwritten = [
            officer.sfu_computing_id
            for (position, officer) in currently_held_executive_positions.items()
        ]

        for unprocessed_officer_sfu_computing_id in unprocessed_officers_sfu_computing_ids:
            if unprocessed_officer_sfu_computing_id in current_executive_officers_not_being_overwritten:
                return False, f"{unprocessed_officer_sfu_computing_id} is being set as an executive in term" \
                              f" {term} despite already holding another executive position for that term"
    return True, None
