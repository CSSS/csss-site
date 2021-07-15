def verify_user_input_has_all_required_fields(election_dict, fields=None):
    """
    Create the error message for indicating if a field is missing

    Keyword Argument
    election_dict -- the dictionary that contains all the user inputs
    fields -- the list of field that need to exist in the dictionary. If there are 2 fields where at least one
     is needed, add them to via a list under one element in fields

    Return
    the error message -- just "" if there are no errors
    """
    error_message = ""
    if fields is not None and type(fields) == list:
        field_exists = False
        for field in fields:
            if type(field) is list:
                number_of_field_options_found = [1 for field_option in field if field_option in election_dict]
                if len(number_of_field_options_found) == 0:
                    error_message += f", {' or '.join(field)}" if field_exists else f"{' or '.join(field)}"
                    field_exists = True
            elif field not in election_dict:
                error_message += f", {field}" if field_exists else f"{field}"
                field_exists = True
    if error_message != "":
        error_message = "It seems that the following field[s] are missing: " + error_message
    return error_message
