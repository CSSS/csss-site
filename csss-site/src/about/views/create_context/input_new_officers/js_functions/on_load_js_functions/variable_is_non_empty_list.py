def variable_is_non_empty_list(obj):
    """
    Indicates if the given list contains at least 1 entry

    Return
    bool -- true if bool is a non-empty list
    """
    return type(obj) is list and len(obj) > 0
