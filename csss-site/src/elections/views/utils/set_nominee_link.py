from django.conf import settings

from about.views.generate_officer_creation_links.officer_creation_link_management import HTML_PASSPHRASE_GET_KEY


def set_nominee_link(nominee_link):
    """
    Update the Nominee Link object so that it contains the nominee link via the `link` attribute

    Keyword Argument
    nominee_link -- the nominee link object

    Return
    the update nominee link object that contains the link attribute
    """
    base_url = f"{settings.HOST_ADDRESS}"
    # this is necessary if the user is testing the site locally and therefore is using the port to access the
    # browser
    if settings.PORT is not None:
        base_url += f":{settings.PORT}"
    base_url += f"{settings.URL_ROOT}about/allow_officer_to_choose_name?"
    nominee_link.link = f"{base_url}{HTML_PASSPHRASE_GET_KEY}={nominee_link.passphrase}"
    return nominee_link
