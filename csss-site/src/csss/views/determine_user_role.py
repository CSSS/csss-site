from csss.views.privilege_validation.obtain_sfuids_for_specified_positions_and_terms import \
    get_current_election_officer_sfuid, get_current_sys_admin_sfuid, \
    get_sfuid_for_officer_in_past_5_terms, get_current_webmaster_or_doa_sfuid


def user_is_officer_in_past_5_terms(request, unprocessed_officers=None, officers=None):
    """
    Determines if the user has been an officer in the past 5 terms

    Keyword Argument
    request -- the django request object
    unprocessed_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    bool -- True if the user has been an officer in the past 5 terms
    """
    if request.user.username == "root":
        return True
    return request.user.username in get_sfuid_for_officer_in_past_5_terms(
        unprocessed_officers=unprocessed_officers, officers=officers
    )


def user_is_current_webmaster_or_doa(request, unprocessed_officers=None, officers=None):
    """
    Determines if the user is the current DoA or Webmaster (or Sys Admin if there is not Webmaster)

    Keyword Argument
    request -- the django request object
    unprocessed_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    bool -- True if the user is the current DoA or Webmaster (or Sys Admin if there is not Webmaster)
    """
    if request.user.username == "root":
        return True
    return request.user.username in get_current_webmaster_or_doa_sfuid(
        unprocessed_officers=unprocessed_officers,
        officers=officers
    )


def user_is_current_sys_admin(request, unprocessed_officers=None, officers=None):
    """
    Determines if the user is the current Sys Admin

    Keyword Argument
    request -- the django request object
    unprocessed_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    bool -- True if the user is the current Sys Admin
    """
    if request.user.username == "root":
        return True
    return request.user.username == get_current_sys_admin_sfuid(unprocessed_officers=unprocessed_officers,
                                                                officers=officers)


def user_is_current_election_officer(request, unprocessed_officers=None, officers=None):
    """
    Determines if the user is the current election officer

    Keyword Argument
    request -- the django request object
    unprocessed_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    bool -- True if the user is the current election officer
    """
    if request.user.username == "root":
        return True
    return request.user.username == get_current_election_officer_sfuid(officers=officers,
                                                                       unprocessed_officers=unprocessed_officers)
