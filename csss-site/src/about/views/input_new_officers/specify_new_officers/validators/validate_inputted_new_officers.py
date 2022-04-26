from about.models import OfficerEmailListAndPositionMapping, NewOfficer
from about.views.input_new_officers.specify_new_officers.validators.validate_discord_id import validate_discord_id
from about.views.input_new_officers.specify_new_officers.validators.validate_sfu_id import validate_sfu_id
from about.views.input_new_officers.specify_new_officers.validators.validate_start_date import validate_start_date


def validate_inputted_new_officers(new_officers_dict):
    selected_positions = []
    discord_ids = []
    sfu_computing_ids = []
    valid_ids = []
    positions = OfficerEmailListAndPositionMapping.objects.all().filter()
    for new_officer in new_officers_dict:
        if 'id' in new_officer:
            if NewOfficer.objects.all().filter(id=new_officer['id']).first() is None:
                del new_officer['id']
            elif new_officer['id'] in valid_ids:
                del new_officer['id']
            else:
                valid_ids.append(new_officer['id'])
        selected_position = new_officer['position_name'].strip()
        if selected_position in selected_positions:
            return False, f"You cannot have more than 1 {selected_position}"
        selected_position = positions.filter(position_name=selected_position).first()
        if selected_position is None:
            return False, f"Invalid position of {selected_position} specified"
        selected_positions.append(selected_position.position_name)
        if len(new_officer['discord_id'].strip()) > 0:
            discord_id = new_officer['discord_id'].strip()
            valid, error_message = validate_discord_id(discord_id)
            if not valid:
                return False, f"invalid error of {error_message} with Discord ID of {discord_id}"
            if selected_position.executive_position:
                if discord_id in discord_ids:
                    return False, f"the discord ID of {discord_id} was entered more than once"
                discord_ids.append(discord_id)
        sfu_computing_id = new_officer['sfu_computing_id'].strip()
        success, error_message = validate_sfu_id(sfu_computing_id)
        if not success:
            return False, error_message
        if selected_position.executive_position:
            if sfu_computing_id in sfu_computing_ids:
                return False, f"the discord ID of {sfu_computing_id} was entered more than once"
            sfu_computing_ids.append(sfu_computing_id)
        if not ('re_use_start_date' in new_officer or 'start_date' in new_officer):
            return False, "One of the position does not have a new date and is not re-using a previous date"
        start_date = new_officer['start_date'].strip()
        success, error_message = validate_start_date(start_date)
        if not success:
            return success, error_message
    return True, None
