from about.models import Officer, Term
from csss.views.privilege_validation.list_of_officer_details_from_past_specified_terms import get_relevant_terms, \
    get_list_of_officer_details_from_past_specified_terms
from resource_management.models import NaughtyOfficer


def get_current_election_officer_sfuid(naughty_officers=None, officers=None):
    relevant_previous_terms = 0
    position_names = ["General Election Officer", "By-Election Officer"]
    return _get_sfuids_for_specified_position_in_specified_terms(
        relevant_previous_terms=relevant_previous_terms, position_names=position_names,
        naughty_officers=naughty_officers, officers=officers
    )


def get_sfuid_for_officer_in_past_5_terms(naughty_officers=None, officers=None):
    return _get_sfuids_for_specified_position_in_specified_terms(
        naughty_officers=naughty_officers, officers=officers
    )


def get_current_sys_admin_or_webmaster_sfuid(naughty_officers=None, officers=None):
    relevant_previous_terms = 0
    position_names = ["Webmaster", "Systems Administrator"]
    return _get_sfuids_for_specified_position_in_specified_terms(
        relevant_previous_terms=relevant_previous_terms, position_names=position_names,
        naughty_officers=naughty_officers, officers=officers
    )


def get_current_sys_admin_sfuid(naughty_officers=None, officers=None):
    relevant_previous_terms = 0
    position_names = ["Systems Administrator"]
    return _get_sfuids_for_specified_position_in_specified_terms(
        relevant_previous_terms=relevant_previous_terms, position_names=position_names,
        naughty_officers=naughty_officers, officers=officers
    )


def get_current_webmaster_or_doa_sfuid(naughty_officers=None, officers=None):
    relevant_previous_terms = 0
    current_webmaster_sfuids = _get_sfuids_for_specified_position_in_specified_terms(
        relevant_previous_terms=relevant_previous_terms, position_names=["Webmaster"],
        naughty_officers=naughty_officers, officers=officers
    )
    webmaster_positions = "Systems Administrator" if len(current_webmaster_sfuids) == 0 else "Webmaster"
    position_names = [webmaster_positions, "Director of Archives"]
    return _get_sfuids_for_specified_position_in_specified_terms(
        relevant_previous_terms=relevant_previous_terms, position_names=position_names,
        naughty_officers=naughty_officers, officers=officers
    )


def _get_sfuids_for_specified_position_in_specified_terms(
        relevant_previous_terms=5, position_names=None,
        naughty_officers=None, officers=None):
    if naughty_officers is None:
        naughty_officers = [naughty_officer.sfuid.strip() for naughty_officer in NaughtyOfficer.objects.all()]
    else:
        naughty_officers = [naughty_officer.sfuid.strip() for naughty_officer in naughty_officers]
    if officers is None:
        all_officers_in_past_term = Officer.objects.all().filter(
            elected_term__in=Term.objects.all().filter(term_number__in=get_relevant_terms(relevant_previous_terms))
        )
    else:
        all_officers_in_past_term = officers.filter(
            elected_term__in=Term.objects.all().filter(term_number__in=get_relevant_terms(relevant_previous_terms))
        )
    return get_list_of_officer_details_from_past_specified_terms(
        position_names=position_names,
        filter_by_sfuid=True, naughty_officers=naughty_officers,
        all_officers_in_relevant_terms=all_officers_in_past_term
    )
