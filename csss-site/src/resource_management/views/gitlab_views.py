import logging

from resource_management.views.current_officer_list import get_past_x_terms_officer_list

logger = logging.getLogger('csss_site')


def create_gitlab_perms():
    """
    Creates a list of all the user who will have gitlab access

    Return
    officer -- Example < sfuid1, sfuid2, sfuid3, sfuid3 >
    """
    sfuids = [officer.sfuid.lower() for officer in get_past_x_terms_officer_list()]
    gitlab_perms = []
    for item in sfuids:
        if item not in gitlab_perms:
            gitlab_perms.append(item)
    return gitlab_perms
