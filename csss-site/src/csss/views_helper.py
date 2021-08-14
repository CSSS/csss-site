import logging

from django.conf import settings

from administration.Constants import CURRENT_WEBMASTER_OR_DOA, OFFICER_IN_PAST_5_TERMS, \
    CURRENT_ELECTION_OFFICER, CURRENT_SYS_ADMIN, CURRENT_SYS_ADMIN_OR_WEBMASTER, USER_SFUID
from administration.cas_session_management import cas_login
from elections.models import Election

ERROR_MESSAGE_KEY = 'error_message'
ERROR_MESSAGES_KEY = 'error_messages'

logger = logging.getLogger('csss_site')


def create_main_context(request, tab):
    """
    creates the main context dictionary

    Keyword Arguments
    request -- the django request object
    tab -- the tab that needs to be specified it the context
    groups -- the groups that need to be checked to see if the user is allowed to certain group privileges

    Return
    context -- the base context dictionary
    """
    cas_login(request)
    elections = Election.objects.all().order_by('-date')
    if len(elections) == 0:
        elections = None
    context = _create_base_context()
    request_path = None
    if request.session.get(USER_SFUID, None) is None:
        request_path = f"https://cas.sfu.ca/cas/login?service=http://{settings.HOST_ADDRESS}"
        if settings.PORT is not None:
            request_path += f":{settings.PORT}"
        request_path += f"{request.path}"

    context.update({
        'username': request.session.get(USER_SFUID, False),
        'cas_login': request_path,
        'tab': tab,
        'election_list': elections,
        CURRENT_WEBMASTER_OR_DOA: request.session.get(CURRENT_WEBMASTER_OR_DOA, False),
        CURRENT_SYS_ADMIN: request.session.get(CURRENT_SYS_ADMIN, False),
        CURRENT_SYS_ADMIN_OR_WEBMASTER: request.session.get(CURRENT_SYS_ADMIN_OR_WEBMASTER, False),
        OFFICER_IN_PAST_5_TERMS: request.session.get(OFFICER_IN_PAST_5_TERMS, False),
        CURRENT_ELECTION_OFFICER: request.session.get(CURRENT_ELECTION_OFFICER, False)
    })
    return context


def create_frosh_context():
    """
    creates the context dictionary for the frosh webpages

    Return
    context -- the frosh webpages context dictionary
    """
    return _create_base_context()


def _create_base_context():
    """
    creates the base context dictionary that contains only the URL_ROOT

    Return
    context -- the base context dictionary

    """
    context = {
        'URL_ROOT': settings.URL_ROOT,
    }
    return context


def there_are_multiple_entries(post_dict, key_to_read):
    """
    Check to see if the given dictionary has an array or a single element at the specified key

    Keyword Argument
    post_dict -- the dictionary to check
    key_to_read -- the key in the dictionary to check

    return:
    True if the key contains an erray of elements rather than just 1 element. or None if that
     key is not in the dictionary
    """
    if key_to_read not in post_dict:
        return None
    return isinstance(post_dict[key_to_read], list)
