from about.models import Officer, Term, UnProcessedOfficer
from csss.views.privilege_validation.list_of_officer_details_from_past_specified_terms import get_relevant_terms, \
    get_list_of_officer_details_from_past_specified_terms


def get_current_election_officer_sfuid(unprocessed_officers=None, officers=None):
    """
    Get the SFUID for the current election officer

    Keyword Arguments
    unprocessed_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    the SFUID for the current election officer
    """
    relevant_previous_terms = 0
    position_names = ["General Election Officer", "By-Election Officer"]
    return _get_sfuids_for_specified_position_in_specified_terms(
        relevant_previous_terms=relevant_previous_terms, position_names=position_names,
        unprocessed_officers=unprocessed_officers, officers=officers, current_officer_only=True
    )


def get_sfuid_for_officer_in_past_5_terms(unprocessed_officers=None, officers=None):
    """
    Get the SFUIDs for any person who has been an officer in the past 5 terms

    Keyword Arguments
    unprocessed_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    a list of SFUIDs for officer who have been officers in the past 5 terms and have updated their bio
    """
    return _get_sfuids_for_specified_position_in_specified_terms(
        unprocessed_officers=unprocessed_officers, officers=officers
    )


def get_current_sys_admin_or_webmaster_sfuid(unprocessed_officers=None, officers=None):
    """
    Get the SFUIDs for any person who is a current sys admin or webmaster

    Keyword Arguments
    unprocessed_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    a list of SFUIDs for officer who are currently a sys admin or webmaster
    """
    relevant_previous_terms = 0
    position_names = ["Webmaster", "Systems Administrator"]
    return _get_sfuids_for_specified_position_in_specified_terms(
        relevant_previous_terms=relevant_previous_terms, position_names=position_names,
        unprocessed_officers=unprocessed_officers, officers=officers
    )


def get_current_sys_admin_sfuid(unprocessed_officers=None, officers=None):
    """
    Get the SFUID for the current sys admin

    Keyword Arguments
    unprocessed_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    the SFUID for the current sys admin
    """
    relevant_previous_terms = 0
    position_names = ["Systems Administrator"]
    return _get_sfuids_for_specified_position_in_specified_terms(
        relevant_previous_terms=relevant_previous_terms, position_names=position_names,
        unprocessed_officers=unprocessed_officers, officers=officers, current_officer_only=True
    )


def get_current_webmaster_or_doa_sfuid(unprocessed_officers=None, officers=None):
    """
    Get the SFUIDs for any person who is a current DoA or Webmaster (or Sys Admin if there is not Webmaster)

    Keyword Arguments
    unprocessed_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers

    Return
    a list of SFUIDs for officer who is currently a DoA or Webmaster (or Sys Admin if there is no Webmaster)
    """
    relevant_previous_terms = 0
    current_webmaster_sfuids = _get_sfuids_for_specified_position_in_specified_terms(
        relevant_previous_terms=relevant_previous_terms, position_names=["Webmaster"],
        unprocessed_officers=unprocessed_officers, officers=officers
    )
    webmaster_positions = "Systems Administrator" if len(current_webmaster_sfuids) == 0 else "Webmaster"
    position_names = [webmaster_positions, "Director of Archives"]
    return _get_sfuids_for_specified_position_in_specified_terms(
        relevant_previous_terms=relevant_previous_terms, position_names=position_names,
        unprocessed_officers=unprocessed_officers, officers=officers
    )


def _get_sfuids_for_specified_position_in_specified_terms(
        relevant_previous_terms=5, position_names=None,
        unprocessed_officers=None, officers=None, current_officer_only=False):
    """
    gets either a list of SFUIDs or the sole applicable SFUID

    Keyword Argument
    relevant_previous_terms - if 0 specified, only get current term
     if 1 is specified get current and previous term and so forth
    position_names -- indicates which officers to narrow the list down to if specified
    unprocessed_officers -- the list of SFUIDs for officer who have not yet added their latest bio
    officers -- all current and past officers
    current_officer_only -- indicates whether to return a list of all the officers that match
     the condition or just the latest one to do so

    Return
    the list of SFUIDs or the sole applicable SFUID based on the parameters
    """
    if unprocessed_officers is None:
        unprocessed_officers = [
            unprocessed_officer.sfu_computing_id.strip() for unprocessed_officer in UnProcessedOfficer.objects.all()
        ]
    else:
        unprocessed_officers = [
            unprocessed_officer.sfu_computing_id.strip() for unprocessed_officer in unprocessed_officers
        ]
    if officers is None:
        all_officers_in_past_term = Officer.objects.all().filter(
            elected_term__in=Term.objects.all().filter(term_number__in=get_relevant_terms(relevant_previous_terms))
        ).order_by('-start_date')
    else:
        all_officers_in_past_term = officers.filter(
            elected_term__in=Term.objects.all().filter(term_number__in=get_relevant_terms(relevant_previous_terms))
        )
    return get_list_of_officer_details_from_past_specified_terms(
        position_names=position_names,
        filter_by_sfuid=True, unprocessed_officers=unprocessed_officers,
        all_officers_in_relevant_terms=all_officers_in_past_term,
        current_officer_only=current_officer_only
    )
