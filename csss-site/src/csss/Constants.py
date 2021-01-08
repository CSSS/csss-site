class Constants:

    # USED IN add_new_position_mapping.py
    POSITION_INDEX = "position_index"

    # USED IN add_new_position_mapping.py AND position_mapping_helper.py
    POSITION_NAME = "position_name"
    POSITION_EMAIL = "position_email"

    # USED IN position_mapping.py AND update_existing_position_mapping.py
    user_select_to_a_position_mapping_option = "action"

    # USED IN update_existing_position_mapping.py
    user_select_to_update_position_mapping = "update"
    user_select_to_delete_position_mapping = "delete"
    user_select_to_un_delete_position_mapping = "un_delete"

    # USED IN input_new_officer_positions.py
    user_selected_to_add_new_officer_position = 'add_new_position_mapping'

    # USED IN github_api.py
    github_exception_team_name_not_unique = 422
    CSSS_GITHUB_ORG_NAME = 'CSSS'
    CSS_GITHUB_ORG_PRIVACY = 'closed'
    time_to_wait_due_to_github_rate_limit = 60

    # USED IN save_new_github_officer_team_mapping.py AND position_mapping_helper.py
    user_selected_to_create_new_github_mapping = 'create_new_github_mapping'
    POSITION_INDEX_KEY = 'position_index'
    TEAM_NAME_KEY = 'team_name'

    # USED IN update_saved_github_mappings.py AND position_mapping_helper.py
    GITHUB_TEAM__ID_KEY = "github_mapping__id"
    user_selected_to_un_delete_github_mapping = 'un_delete_github_mapping'
    user_selected_to_mark_github_mapping_for_deletion = 'mark_for_deletion_github_mapping'
    user_selected_to_update_github_mapping = 'update_github_mapping'
    user_selected_to_delete_github_mapping = 'delete_github_mapping'

    # USED IN position_mapping_helper.py
    SAVED_GITHUB_MAPPINGS = 'github_teams'
    OFFICER_POSITION_AVAILABLE_FOR_GITHUB_MAPPINGS = 'github_position_mapping'
    SAVED_OFFICER_POSITIONS = 'saved_officer_positions'
    GITHUB_MAPPING_SELECTED_OFFICER_POSITION_KEY = 'github_mapping_selected_officer_position'

    # USED IN update_saved_position_mappings.py AND position_mapping_helper.py
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__ID = "officer_email_list_and_position_mapping__id"
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_INDEX = "officer_email_list_and_position_mapping__position_index"
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__POSITION_NAME = "officer_email_list_and_position_mapping__position_name"
    OFFICER_EMAIL_LIST_AND_POSITION_MAPPING__EMAIL_LIST_ADDRESS = \
        "officer_email_list_and_position_mapping__email_list_address"
    DELETE_POSITION_MAPPING_KEY = 'delete_position_mapping'
    UN_DELETED_POSITION_MAPPING_KEY = 'un_delete_position_mapping'
    UPDATE_POSITION_MAPPING_KEY = 'update_position_mapping'

    # USED IN save_new_github_officer_team_mapping.py AND update_saved_github_mappings.py AND position_mapping_helper.py
    GITHUB_TEAM__TEAM_NAME_KEY = "github_mapping__team_name"