import logging

from django.conf import settings
from django.http import HttpResponseRedirect

ERROR_MESSAGE_KEY = 'error_message'

logger = logging.getLogger('csss_site')


def create_context(request, tab, groups=None):
    if groups is None:
        groups = list(request.user.groups.values_list('name', flat=True))
    context = {
        'authenticated': request.user.is_authenticated,
        'officer': ('officer' in groups),
        'election_officer': ('election_officer' in groups),
        'staff': request.user.is_staff,
        'username': request.user.username,
        'tab': tab,
        'URL_ROOT': settings.URL_ROOT
    }
    return context


def verify_access_logged_user_and_create_context(request, tab):
    groups = list(request.user.groups.values_list('name', flat=True))
    context = create_context(request, tab, groups)
    if not ('election_officer' in groups or request.user.is_staff or 'officer' in groups):
        return HttpResponseRedirect(
            '/error'), "You are not authorized to access this page", None
    return None, None, context


def there_are_multiple_entries(post_dict, key_to_read):
    return len(post_dict[key_to_read][0]) > 1
