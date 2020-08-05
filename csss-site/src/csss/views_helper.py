import logging

from django.conf import settings
from django.http import HttpResponseRedirect

from elections.models import NominationPage

ERROR_MESSAGE_KEY = 'error_message'

logger = logging.getLogger('csss_site')


def create_main_context(request, tab, groups=None):
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    nom_pages = NominationPage.objects.all().order_by('-date')
    if len(nom_pages) == 0:
        nom_pages = None
    context = _create_base_context()
    context.update({
        'authenticated': request.user.is_authenticated,
        'authenticated_officer': ('officer' in groups),
        'election_officer': ('election_officer' in groups),
        'staff': request.user.is_staff,
        'username': request.user.username,
        'tab': tab,
        'nom_pages': nom_pages
    })
    return context


def create_frosh_context():
    return _create_base_context()


def _create_base_context():
    context = {
        'URL_ROOT': settings.URL_ROOT,
    }
    return context


def verify_access_logged_user_and_create_context_for_elections(request, tab):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = create_main_context(request, tab, groups)
    if not ('election_officer' in groups or request.user.is_staff):
        return HttpResponseRedirect(
            '/error'), "You are not authorized to access this page", None
    return None, None, context


def verify_access_logged_user_and_create_context(request, tab):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = create_main_context(request, tab, groups)
    if not (request.user.is_staff or 'officer' in groups):
        return HttpResponseRedirect(
            '/error'), "You are not authorized to access this page", None
    return None, None, context


def there_are_multiple_entries(post_dict, key_to_read):
    return len(post_dict[key_to_read][0]) > 1
