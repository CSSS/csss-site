import logging

from csss.views.privilege_validation.list_of_officer_details_from_past_specified_terms import \
    get_list_of_officer_details_from_past_specified_terms

logger = logging.getLogger('csss_site')


def create_gitlab_perms():
    """
    Creates a list of all the user who will have gitlab access

    Return
    officer -- Example < sfuid1, sfuid2, sfuid3, sfuid3 >
    """
    sfuids = [officer.sfuid.lower() for officer in get_list_of_officer_details_from_past_specified_terms()]
    gitlab_perms = []
    for item in sfuids:
        if item not in gitlab_perms:
            gitlab_perms.append(item)
    return gitlab_perms
