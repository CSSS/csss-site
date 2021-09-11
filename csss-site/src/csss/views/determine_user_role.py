from csss.views.privilege_validation.obtain_sfuids_for_specified_positions_and_terms import \
    get_current_election_officer_sfuid, get_current_sys_admin_sfuid, \
    get_sfuid_for_officer_in_past_5_terms, get_current_webmaster_or_doa_sfuid


def user_is_officer_in_past_5_terms(request, naughty_officers=None, officers=None):
    return request.user.username in get_sfuid_for_officer_in_past_5_terms(
        naughty_officers=naughty_officers, officers=officers
    )


def user_is_current_webmaster_or_doa(request, naughty_officers=None, officers=None):
    return request.user.username in get_current_webmaster_or_doa_sfuid(
        naughty_officers=naughty_officers, officers=officers
    )


def user_is_current_sys_admin(request, naughty_officers=None, officers=None):
    return request.user.username in get_current_sys_admin_sfuid(naughty_officers=naughty_officers, officers=officers)


def user_is_current_election_officer(request, naughty_officers=None, officers=None):
    return request.user.username in get_current_election_officer_sfuid(naughty_officers, officers)
