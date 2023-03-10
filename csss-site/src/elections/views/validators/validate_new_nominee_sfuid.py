from about.views.input_new_officers.specify_new_officers.validators.validate_sfu_id import validate_sfu_id


def validate_new_nominee_sfuid(new_nominee_sfuids):
    """
    Ensure that the new nominee links specified by the election officer have a valid sfuID

    Keyword Argument
    new_nominee_sfuids -- the new nominee SFU IDs specified by the user that has to be validated

    Return
    bool - True or False
    error_message -- None if there is no error message, or a string
    """
    if new_nominee_sfuids is not None and type(new_nominee_sfuids) == str:
        for new_nominee_sfuid in new_nominee_sfuids.split("\r\n"):
            if new_nominee_sfuid.strip() != "":
                new_nominee_sfuid = new_nominee_sfuid.strip()
                success, error_message = validate_sfu_id(new_nominee_sfuid)
                if not success:
                    return success, error_message
