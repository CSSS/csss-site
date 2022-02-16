def validate_user_command(new_officers_dict):
    return 'save_or_update_new_officers' in new_officers_dict and new_officers_dict['save_or_update_new_officers'] == 'Save/Create All The New Officers Informations'
