def validate_websurvey_link(link):
    """
    Verifies that the websurvey link is valid

    Keyword Argument
    link -- the link to validate

    Return
    Bool -- True or False
    error_message -- String or None
    """
    if _validate_http_link(link):
        return True, None
    else:
        return False, "The websurvey link des not start with \"http://\" or \"https://\""


def validate_link_for_nominee_social_media(link, link_type, nom_name):
    """
    Verifies that the social media link for a nominee is valid

    Keyword Argument
    link -- the link to validate
    link_type -- the link type
    nom_name -- the name that the link belongs to

    Return
    Bool -- True or False
    error_message -- String or None
    """
    if _validate_http_link(link):
        return True, None
    else:
        return False, f"the {link_type} link for nominee {nom_name} does not start with \"http://\" or \"https://\""


def _validate_http_link(link):
    """
    Verifies that the link is valid, which means it either starts with "http://" or "https://" or is NONE

    Keyword Argument
    link -- the link to validate

    Return
    Bool -- True or False
    """
    return link[:7] == "http://" or link[:8] == "https://" or link == "NONE"
