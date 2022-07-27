from about.models import OfficerEmailListAndPositionMapping, NewOfficer, Officer, Term
from about.views.input_new_officers.specify_new_officers.validators.validate_discord_id import validate_discord_id
from about.views.input_new_officers.specify_new_officers.validators.validate_sfu_id import validate_sfu_id
from about.views.input_new_officers.specify_new_officers.validators.validate_start_date import validate_start_date


def validate_inputted_new_officers(inputted_term, inputted_year, new_officers=None):
    """
    validates the inputted new officers position_names, full_name, discord_id, sfu_computing_id, start_date
    and ensures that any officer is not being used for more than 1 executive officer in any given term

    Keyword Argument
    inputted_term -- the term that the new officers were voted in
    inputted_year -- the year that the new officers were voted in
    new_officers -- the new officers that the user has inputted

    Return
    bool -- indicator of whether the validation was successful
    error_message -- whatever error message there was as a result of the validation, or None
    """
    if new_officers is None:
        return True, None
    selected_positions = []
    discord_ids = []
    new_officers_sfu_computing_ids = []
    valid_ids = []
    positions = OfficerEmailListAndPositionMapping.objects.all()

    # will create a map of the currently filled executive positions and who is filling those roles to
    # determine if anyone is being given 2+ executive roles in the same term
    term = Term.objects.all().filter(term=inputted_term, year=inputted_year).first()
    currently_held_executive_positions = {}
    if term is not None:
        current_officers_in_selected_term = Officer.objects.all().filter(elected_term=term).order_by('start_date')
        for current_officer_in_selected_term in current_officers_in_selected_term:
            selected_position = positions.filter(position_name=current_officer_in_selected_term.position_name).first()
            if selected_position is not None and selected_position.executive_position:
                currently_held_executive_positions[current_officer_in_selected_term.position_name] = \
                    current_officer_in_selected_term

    for new_officer in new_officers:
        if 'id' in new_officer:
            if NewOfficer.objects.all().filter(id=new_officer['id']).first() is None:
                del new_officer['id']
            elif new_officer['id'] in valid_ids:
                del new_officer['id']
            else:
                valid_ids.append(new_officer['id'])
        selected_position_name = new_officer['position_name'].strip()
        if selected_position_name in selected_positions:
            return False, f"You cannot have more than 1 {selected_position_name}"
        selected_position = positions.filter(position_name=selected_position_name).first()
        if selected_position is None:
            return False, f"Invalid position of {selected_position} specified"
        officer_name = new_officer['full_name'].strip()
        if ' ' not in officer_name:
            return False, f"Could not detect a full name for \"{officer_name}\" [first AND last name]"
        selected_positions.append(selected_position_name)
        if len(new_officer['discord_id'].strip()) > 0:
            discord_id = new_officer['discord_id'].strip()
            valid, error_message = validate_discord_id(discord_id)
            if not valid:
                return False, f"invalid error of {error_message} with Discord ID of {discord_id}"
            if discord_id in discord_ids:
                return False, f"the discord ID of {discord_id} was entered more than once"
            discord_ids.append(discord_id)
        sfu_computing_id = new_officer['sfu_computing_id'].strip()
        success, error_message = validate_sfu_id(sfu_computing_id)
        if not success:
            return False, error_message
        if selected_position.executive_position:
            if sfu_computing_id in new_officers_sfu_computing_ids:
                return False, f"Someone cannot hold 2+ executive position in a given term"
            new_officers_sfu_computing_ids.append(sfu_computing_id)
        if not ('re_use_start_date' in new_officer or 'start_date' in new_officer):
            return False, "One of the position does not have a new date and is not re-using a previous date"
        start_date = new_officer['start_date'].strip()
        success, error_message = validate_start_date(start_date)
        if not success:
            return success, error_message
        if selected_position_name in currently_held_executive_positions:
            del currently_held_executive_positions[selected_position.position_name]

    if term is not None:
        # list of all the executive offiers that will retain their executive status even after all the new officers
        # are processed
        current_executive_officers_not_being_overwritten = [
            officer.sfuid
            for (position, officer) in currently_held_executive_positions.items()
        ]

        for new_officer_sfu_computing_id in new_officers_sfu_computing_ids:
            if new_officer_sfu_computing_id in current_executive_officers_not_being_overwritten:
                return False, f"{new_officer_sfu_computing_id} is being set as an executive in term {term} despite" \
                              f" already holding another executive position for that term"
    return True, None
