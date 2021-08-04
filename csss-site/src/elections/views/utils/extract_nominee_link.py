from about.views.generate_officer_creation_links.officer_creation_link_management import HTML_PASSPHRASE_GET_KEY
from csss.views_helper import create_main_context
from elections.models import NomineeLink


def verify_passphrase_access_and_create_context(request, tab):
    """
    Verifies that the user is allowed to access the request page depending on their passphrase

    Keyword Arguments
    request -- the django request object
    tab -- the indicator of what section the html page belongs to

    Returns
    render redirect -- the page to direct to if an error is encountered with the passphrase
    context -- the context that gets returned if no error is detected
    error_message -- the error message to display on the error page
    new_officer_details -- the details for the officer who needs to be saved
    """
    nominee_link_passphrase = request.GET.get(HTML_PASSPHRASE_GET_KEY, None)
    if nominee_link_passphrase is not None:
        new_officer_details = NomineeLink.objects.all().filter(passphrase=nominee_link_passphrase)
        logger.info(
            "[about/officer_creation_link_management.py verify_passphrase_access_and_create_context()] "
            f"len(passphrase) = '{len(new_officer_details)}'"
        )
        if len(new_officer_details) == 0:
            error_message = "You did not supply a passphrase that matched any in the records"
            return HttpResponseRedirect(f'{settings.URL_ROOT}error'), None, error_message, None
        new_officer_detail = new_officer_details[0]
        logger.info(
            f"[about/officer_creation_link_management.py verify_passphrase_access_and_create_context()]"
            f" new_officer_detail.used = '{new_officer_detail.used}'")
        if new_officer_detail.used:
            error_message = "the passphrase supplied has already been used"
            return HttpResponseRedirect(f'{settings.URL_ROOT}error'), None, error_message, None
    else:
        return HttpResponseRedirect(f'{settings.URL_ROOT}error'), None, "You did not supply a passphrase", None
    groups = list(request.user.groups.values_list('name', flat=True))
    context = create_main_context(request, tab, groups)
    return None, context, None, new_officer_detail