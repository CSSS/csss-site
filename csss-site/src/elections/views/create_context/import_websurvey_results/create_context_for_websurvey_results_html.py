from csss.views.context_creation.error_htmls.create_context_for_html_snippet_for_general_error_validations import \
    create_context_for_html_snippet_for_general_error_validations_html
from elections.views.Constants import NO_CONFIDENCE_NAME, SKIPPED_VOTE
from elections.views.import_websurvey_results.get_dict_for_election_position_name_mapping import \
    get_dict_for_election_position_name_mapping


def create_context_for_websurvey_results_html(context, election_obj, import_websurvey_data=False,
                                              map_websurvey_nominees=False, map_websurvey_positions=False,
                                              pending_voter_choices=None, errors=None,
                                              election_position_name_mappings=None,
                                              selected_position_mappings=None):
    """
    populates the context dictionary that is used by
     elections/templates/elections/websurvey_results.html

    Keyword Arguments
    context -- the context dictionary that has to be populated for the websurvey_results.html
    election_obj -- the election that is having its results imported
    import_websurvey_data -- the user is interacting with the page for uploading the websurvey export file
    map_websurvey_nominees -- the user is interacting with the page for mapping the websurvey nominees found with
     the nominees associated with the election
    map_websurvey_positions -- the user is interacting with the page for mapping a websurvey question/column with
     one of the positions being voted on in the election
    pending_voter_choices -- list of all PendingVoterChoices objects for the selected election
    errors -- error message to display
    election_position_name_mappings -- the dict that is created by get_dict_for_election_position_name_mapping
    selected_position_mappings -- the user's current selection of websurvey position mappings
    """
    if errors is not None:
        create_context_for_html_snippet_for_general_error_validations_html(context, errors)
    context['election'] = election_obj
    context['import_websurvey_data'] = import_websurvey_data
    context['map_websurvey_nominees'] = map_websurvey_nominees
    context['map_websurvey_positions'] = map_websurvey_positions
    if map_websurvey_nominees:
        nominee_names = list(set(election_obj.nominee_set.all().values_list('full_name', flat=True)))
        nominee_names.sort()
        if NO_CONFIDENCE_NAME in nominee_names:
            nominee_names.remove(NO_CONFIDENCE_NAME)
        if NO_CONFIDENCE_NAME not in nominee_names:
            nominee_names.insert(0, NO_CONFIDENCE_NAME)
        context['nominee_names'] = nominee_names.copy()
        if SKIPPED_VOTE not in nominee_names:
            nominee_names.append(SKIPPED_VOTE)
        if pending_voter_choices is not None and nominee_names is not None:
            context['websurvey_results_nominee_names'] = list(set(
                pending_voter_choices.exclude(full_name__in=nominee_names).values_list('full_name', flat=True)
            ))
        else:
            if errors is None:
                errors = []
            error_message = (
                "Following necessary parameters were not passed to context creation for mapping websurvey"
                " nominees: "
            )
            if nominee_names is None:
                error_message += "nominee_names"
            if pending_voter_choices is None:
                if nominee_names is None:
                    error_message += ", "
                error_message += "pending_voter_choices"
            errors.append(error_message)
            create_context_for_html_snippet_for_general_error_validations_html(context, errors)
    elif map_websurvey_positions:
        if election_position_name_mappings is None:
            if pending_voter_choices is not None and selected_position_mappings is not None:
                election_position_name_mappings = get_dict_for_election_position_name_mapping(
                    election_obj, pending_voter_choices, selected_position_mappings=selected_position_mappings
                )
            else:
                if errors is None:
                    errors = []
                error_message = (
                    "Following necessary parameters were not passed to context creation for mapping websurvey"
                    " positions: "
                )
                if pending_voter_choices is None:
                    error_message += "pending_voter_choices"
                if selected_position_mappings is None:
                    if pending_voter_choices is None:
                        error_message += ", "
                    error_message += "selected_position_mappings"
                errors.append(error_message)
                create_context_for_html_snippet_for_general_error_validations_html(context, errors)
        context['election_position_name_mappings'] = election_position_name_mappings
