import logging

logger = logging.getLogger('csss_site')


def determine_changes_for_exec_discord_group_role_validation(
    user_id__user_obj, role_id__list_of_users, role_id__role, members_id__role_ids,
    discord_id_for_users_that_should_be_in_exec_discord_group_role,
        exec_discord_role_id):
    """
    Populates/Updates members_id__role_ids to reflect the changes needed to ensure only the current officers have
     the Execs discord group role

    Keyword Arguments
    user_id_dictionary -- a dictionary where the key is the discord user id and the value is the
     corresponding user object
    role_id__list_of_users -- a dictionary where the key is the discord_role_id and the value is a
     list of the users in that role
    members_id__role_ids -- the dict that will be updated with all users who have to have their roles updates
     to either remove an exec-associated discord role or assign them with a exec-associated discord dole
    discord_id_for_users_that_should_be_in_exec_discord_group_role -- a list of all the discord user IDs that have
     to have the Execs discord group role
    exec_discord_role_id -- the role id for the discord Execs role
    """
    users_in_executive_discord_group_role = role_id__list_of_users[exec_discord_role_id]
    for user_in_executive_discord_group_role in users_in_executive_discord_group_role:
        user_in_executive_discord_group_role_id = user_in_executive_discord_group_role['user']['id']
        user_not_yet_added_to_list_of_users_that_should_be_in_exec_group_role = (
            user_in_executive_discord_group_role_id
            not in discord_id_for_users_that_should_be_in_exec_discord_group_role
        )
        if user_not_yet_added_to_list_of_users_that_should_be_in_exec_group_role:
            if user_in_executive_discord_group_role_id not in members_id__role_ids:
                user_in_executive_discord_group_role['roles'].remove(exec_discord_role_id)
                members_id__role_ids[user_in_executive_discord_group_role_id] = {
                    "username": user_in_executive_discord_group_role['user']['username'],
                    "roles": {
                        role_id__role[role]['name']: role
                        for role in user_in_executive_discord_group_role['roles']
                    }
                }
                username = user_in_executive_discord_group_role['user']['username']
                logger.info(
                    "[about/determine_changes_for_exec_discord_group_role_validation.py() ] removing role "
                    f"{role_id__role[exec_discord_role_id]['name']}({exec_discord_role_id}) from user"
                    f" {username}({user_in_executive_discord_group_role_id})"
                )
            else:
                users_roles_1 = list(members_id__role_ids[user_in_executive_discord_group_role_id]['roles'].values())
                if exec_discord_role_id in users_roles_1:
                    role_name = role_id__role[exec_discord_role_id]['name']
                    del members_id__role_ids[user_in_executive_discord_group_role_id]['roles'][role_name]
                    logger.info(
                        "[about/determine_changes_for_exec_discord_group_role_validation.py() ] removing role "
                        f"{role_name}({exec_discord_role_id}) from user "
                        f"{user_id__user_obj[user_in_executive_discord_group_role_id]['user']['username']}"
                        f"({user_in_executive_discord_group_role_id})"
                    )
    for user_that_should_be_in_discord_role in discord_id_for_users_that_should_be_in_exec_discord_group_role:
        discord_ids_for_users_in_executive_role = [
            user['user']['id'] for user in users_in_executive_discord_group_role
        ]
        if user_that_should_be_in_discord_role not in discord_ids_for_users_in_executive_role:
            if user_that_should_be_in_discord_role not in members_id__role_ids:
                members_id__role_ids[user_that_should_be_in_discord_role] = \
                    {"username": user_id__user_obj[user_that_should_be_in_discord_role]['user']['username'],
                     "roles": user_id__user_obj[user_that_should_be_in_discord_role]['roles']}
            members_id__role_ids[user_that_should_be_in_discord_role]['roles'].append(exec_discord_role_id)
            logger.info(
                "[about/determine_changes_for_exec_discord_group_role_validation.py() ] add role "
                f"{exec_discord_role_id} to user {user_that_should_be_in_discord_role}"
            )
