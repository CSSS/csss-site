import re

from elections.views.Constants import NA_STRING


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


def _validate_http_link(link):
    """
    Verifies that the link is valid, which means it either starts with "http://" or "https://" or is NA

    Keyword Argument
    link -- the link to validate

    Return
    Bool -- True or False
    """
    return link[:7] == "http://" or link[:8] == "https://" or link == NA_STRING


def validate_facebook_link(link, nom_name):
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
    if link == NA_STRING:
        return True, None
    if not re.match(r"^https?://(www\.)?facebook.com/\w+$", link):
        error_message = (
            f"Invalid Facebook link of \"{link}\" detected for nominee {nom_name}. "
            f"Don't forgot to start with \"http://\" or \"https://\""
        )
        return False, error_message
    return True, None


def validate_instagram_link(link, nom_name):
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
    if link == NA_STRING:
        return True, None
    if not re.match(r"^https?://(www\.)?instagram.com/\w+/?$", link):
        error_message = (
            f"Invalid Instagram link of \"{link}\" detected for nominee {nom_name}. "
            f"Don't forgot to start with \"http://\" or \"https://\""
        )
        return False, error_message
    return True, None


def validate_linkedin_link(link, nom_name):
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
    if link == NA_STRING:
        return True, None
    if not re.match(r"^https?://(www\.)?linkedin.com/in/\w+$", link):
        error_message = (
            f"Invalid LinkedIn link of \"{link}\" detected for nominee {nom_name}. "
            f"Don't forgot to start with \"http://\" or \"https://\""
        )
        return False, error_message
    return True, None
