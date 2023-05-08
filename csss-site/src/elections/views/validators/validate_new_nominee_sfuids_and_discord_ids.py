from about.views.input_new_officers.specify_new_officers.validators.validate_discord_id import validate_discord_id
from about.views.input_new_officers.specify_new_officers.validators.validate_sfu_id import validate_sfu_id
from elections.views.Constants import NA_STRING


def validate_new_nominee_sfuids_and_discord_ids(new_nominee_sfuids_and_discord_ids):
    """
    Ensure that the new nominee links specified by the election officer have a valid sfuID and discord ID

    Keyword Argument
    new_nominee_sfuids_and_discord_ids -- the new nominee SFU IDs and discord IDs specified by the
    user that has to be validated

    Return
    bool - True or False
    error_message -- None if there is no error message, or a string
    """
    if new_nominee_sfuids_and_discord_ids is not None and type(new_nominee_sfuids_and_discord_ids) == str:
        for new_nominee_sfuids_and_discord_id in new_nominee_sfuids_and_discord_ids.split("\r\n"):
            if new_nominee_sfuids_and_discord_id.strip() != "":
                if "," not in new_nominee_sfuids_and_discord_ids:
                    error_message = (
                        "could not find the entry for SFU ID and Discord ID for Nominee Link Entry "
                        f"\"{new_nominee_sfuids_and_discord_ids}\", "
                        f"please do <SFU_ID>,<Discord ID> on each line, or NA if user has no Discord ID"
                    )
                    return False, error_message
                new_nominee_sfuid = new_nominee_sfuids_and_discord_id.split(",")[0].strip()
                new_nominee_discord_id = new_nominee_sfuids_and_discord_id.split(",")[1].strip()
                success, error_message = validate_sfu_id(new_nominee_sfuid)
                if not success:
                    return success, error_message
                if new_nominee_discord_id != NA_STRING:
                    success, error_message = validate_discord_id(new_nominee_discord_id)
                    if not success:
                        return success, error_message
    return True, None
