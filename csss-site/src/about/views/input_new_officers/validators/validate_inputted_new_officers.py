from about.models import OfficerEmailListAndPositionMapping
from about.views.input_new_officers.validators.validate_discord_id import validate_discord_id
from about.views.input_new_officers.validators.validate_sfu_id import validate_sfu_id
from about.views.input_new_officers.validators.validate_start_date import validate_start_date


def validate_inputted_new_officers(new_officers_dict):
    selected_positions = []
    discord_ids = []
    sfu_computing_ids = []
    positions = OfficerEmailListAndPositionMapping.objects.all().filter()
    for new_officer in new_officers_dict:
        selected_position = new_officer['selected_position']
        if selected_position in selected_positions:
            return False, f"You cannot have more than 1 {selected_position}"
        if positions.filter(position_name=selected_position).first() is None:
            return False, f"Invalid position of {selected_position} specified"
        if len(new_officer['discord_id'].strip()) == 0:
            discord_id = new_officer['discord_id']
            valid, error_message = validate_discord_id(discord_id)
            if not valid:
                return False, f"invalid error of {error_message} with Discord ID of {discord_id}"
            if discord_id in discord_ids:
                return False, f"the discord ID of {discord_id} was entered more than once"
        sfu_computing_id = new_officer['sfu_computing_id']
        if not validate_sfu_id(sfu_computing_id):
            return False, f"Invalid SFUId of {sfu_computing_id} was entered"
        if sfu_computing_id in sfu_computing_ids:
            return False, f"the discord ID of {sfu_computing_id} was entered more than once"
        sfu_computing_ids.append(sfu_computing_id)
        if 're_use_start_date' in new_officer and 'start_date' in new_officer:
            return False, "One of the position is both specifying a new date and is set to re-use a previous date"
        if not ('re_use_start_date' in new_officer or 'start_date' in new_officer):
            return False, "One of the position does not have a new date and is not re-using a previous date"
        if 'start_date' in new_officer:
            start_date = new_officer['start_date']
            success, error_message = validate_start_date(start_date)
            if not success:
                return success, error_message
    return True, None
