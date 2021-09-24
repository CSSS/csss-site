from csss.views.privilege_validation.obtain_sfuids_for_specified_positions_and_terms import \
    get_current_election_officer_sfuid, get_current_sys_admin_sfuid, \
    get_sfuid_for_officer_in_past_5_terms, get_current_webmaster_or_doa_sfuid


def user_is_officer_in_past_5_terms(request, naughty_officers=None, officers=None):
    """
    Determines if the user has been an officer in the past 5 terms

    Keyword Argument
    request -- the django request object
    naughty_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    bool -- True if the user has been an officer in the past 5 terms
    """
    return request.user.username in get_sfuid_for_officer_in_past_5_terms(
        naughty_officers=naughty_officers, officers=officers
    )


def user_is_current_webmaster_or_doa(request, naughty_officers=None, officers=None):
    """
    Determines if the user is the current DoA or Webmaster (or Sys Admin if there is not Webmaster)

    Keyword Argument
    request -- the django request object
    naughty_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    bool -- True if the user is the current DoA or Webmaster (or Sys Admin if there is not Webmaster)
    """
    return request.user.username in get_current_webmaster_or_doa_sfuid(
        naughty_officers=naughty_officers, officers=officers
    )


def user_is_current_sys_admin(request, naughty_officers=None, officers=None):
    """
    Determines if the user is the current Sys Admin

    Keyword Argument
    request -- the django request object
    naughty_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    bool -- True if the user is the current Sys Admin
    """
    return request.user.username == get_current_sys_admin_sfuid(naughty_officers=naughty_officers, officers=officers)


def user_is_current_election_officer(request, naughty_officers=None, officers=None):
    """
    Determines if the user is the current election officer

    Keyword Argument
    request -- the django request object
    naughty_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    bool -- True if the user is the current election officer
    """
    return request.user.username == "root" or \
        request.user.username == get_current_election_officer_sfuid(naughty_officers, officers)
