from django.http import HttpResponseRedirect
from django.shortcuts import render
import logging

logger = logging.getLogger('csss_site')

from administration.models import ProcessNewOfficer


def create_context(request, tab, groups=None):
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'authenticated': request.user.is_authenticated,
        'Exec': ('Exec' in groups),
        'ElectionOfficer': ('ElectionOfficer' in groups),
        'Staff': request.user.is_staff,
        'Username': request.user.username,
        'tab': tab
    }
    return context


def verify_access_logged_user_and_create_context(request, tab):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = create_context(request, tab, groups)
    if not ('ElectionOfficer' in groups or request.user.is_staff or 'Exec' in groups):
        return render(request, 'administration/invalid_access.html', context), None
    return None, context


def verify_passphrase_access_and_create_context(request, tab):
    if 'passphrase' in request.GET or 'passphrase' in request.POST or 'passphrase' in request.session:
        if 'passphrase' in request.GET:
            passphrase = request.GET['passphrase']
        elif 'passphrase' in request.POST:
            passphrase = request.POST['passphrase']
        elif 'passphrase' in request.session:
            passphrase = request.session['passphrase']
            del request.session['passphrase']

        passphrase = ProcessNewOfficer.objects.all().filter(passphrase=passphrase)
        logger.info(
            f"[administration/views_helper.py verify_passphrase_access_and_create_context()] len(passphrase) = '{len(passphrase)}'")
        if len(passphrase) == 0:
            return HttpResponseRedirect(
                '/about/bad_passphrase'), None, "You did not supply a passphrase that matched any" \
                                                " in the records", None
        logger.info(
            f"[administration/officer_views.py verify_passphrase_access_and_create_context()] passphrase["
            f"0].used = '{passphrase[0].used}'")
        if passphrase[0].used:
            return HttpResponseRedirect('/about/bad_passphrase'), None, "the passphrase supplied has already been used", None
    else:
        return HttpResponseRedirect('/about/bad_passphrase'), None, "You did not supply a passphrase", None
    groups = list(request.user.groups.values_list('name', flat=True))
    context = create_context(request, tab, groups)
    return None, context, None, passphrase[0]


def there_are_multiple_entries(post_dict, key_to_read):
    return len(post_dict[key_to_read][0]) > 1
