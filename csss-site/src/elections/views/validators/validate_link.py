def validate_http_link(link, link_type, nom_name=None):
    """
    Verifies that the link is valid, which means it either starts with "http://" or "https://" or is NONE

    Keyword Argument
    link -- the link to validate
    link_type -- the link type
    nom_name -- the name that the link belongs to, if its not a websurvey link

    Return
    Bool -- True or False
    error_message -- String or None
    """
    success = link[:7] == "http://" or link[:8] == "https://" or link == "NONE"
    if not success:
        if nom_name is None:
            return success, f"The {link_type} link des not start with \"http://\" or \"https://\""
        else:
            return success, f"the {link_type} link for nominee {nom_name} does " \
                            f"not start with \"http://\" or \"https://\""
    return success, None
