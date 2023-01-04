from about.models import Officer
from csss.setup_logger import Loggers


def determine_changes_for_position_specific_discord_role_validation(
    user_id__user_obj, role_id__list_of_users, role_id__role, officer_discord_id__officer_full_name,
    exec_discord_role_id, members_id__role_ids,
    discord_id_for_users_that_should_be_in_exec_discord_group_role,
        position_infos, matching_executive_roles, current_officers):
    """
    Populates members_id__role_ids, discord_id_for_users_that_should_be_in_exec_discord_group_role
    with the dictionary where the key is the discord user id and the value is the list of roles they need to have
    and the list of discord user IDS of users who have to be in the Execs discord group role respectively

    Keyword Arguments
    user_id_dictionary -- a dictionary where the key is the discord user id and the value is the
     corresponding user object
    role_id__list_of_users -- a dictionary where the key is the discord_role_id and the value is a
     list of the users in that role
    members_id__role_ids -- the dict that will be updated with all users who have to have their roles updates
     to either remove an exec-associated discord role or assign them with a exec-associated discord dole
    discord_id_for_users_that_should_be_in_exec_discord_group_role -- a list that will be populated with the list
     of discord IDs for the users who have to be the ones in the Execs discord group role
    position_infos -- queryset of all the current position mappings
    matching_executive_roles -- a dictionary where the key is the role name and the value is the role object
    current_officers -- a queryset of officers in the current term

    """
    logger = Loggers.get_logger()
    for (executive_discord_role_name, executive_discord_role_obj) in matching_executive_roles.items():
        positions_that_map_to_the_discord_role = position_infos.filter(
            discord_role_name=executive_discord_role_name
        )
        position_is_executive_officer = positions_that_map_to_the_discord_role.first().executive_officer
        positions_that_map_to_the_discord_role = list(
            positions_that_map_to_the_discord_role.values_list('position_name', flat=True)
        )
        officers_that_should_be_in_discord_role = current_officers.filter(
            position_name__in=positions_that_map_to_the_discord_role
        )
        list_of_officer_ids_that_belong_to_discord_role = list(
            officers_that_should_be_in_discord_role.values_list('discord_id', flat=True)
        )
        if executive_discord_role_obj['id'] in role_id__list_of_users:  # in case the role currently has no users
            users_currently_in_executive_discord_role = role_id__list_of_users[executive_discord_role_obj['id']]
            for user_currently_in_executive_discord_role in users_currently_in_executive_discord_role:
                discord_id_for_user_currently_in_executive_discord_role = (
                    user_currently_in_executive_discord_role['user']['id']
                )
                user_currently_in_discord_role_they_should_not_be_in = (
                    discord_id_for_user_currently_in_executive_discord_role not in
                    list_of_officer_ids_that_belong_to_discord_role
                )
                if user_currently_in_discord_role_they_should_not_be_in:
                    if discord_id_for_user_currently_in_executive_discord_role not in members_id__role_ids:
                        # if the user is currently in a role that they don't belong to and don't have an entry in
                        # the members_id__role_ids dictionary
                        users_current_roles = user_currently_in_executive_discord_role['roles'].copy()
                        users_current_roles.remove(executive_discord_role_obj['id'])
                        users_roles = {
                            role_id__role[role]['name']: role
                            for role in users_current_roles
                        }
                        members_id__role_ids[discord_id_for_user_currently_in_executive_discord_role] = {
                            "username": user_currently_in_executive_discord_role['user']['username'],
                            "roles": users_roles
                        }

                        executive_officer_discord_id_not_added_to_map = (
                            discord_id_for_user_currently_in_executive_discord_role
                            not in officer_discord_id__officer_full_name
                        )
                        if executive_officer_discord_id_not_added_to_map:
                            officer = Officer.objects.all().filter(
                                discord_id=discord_id_for_user_currently_in_executive_discord_role
                            ).first()
                            officer_full_name = officer.full_name if officer is not None else None
                        else:
                            officer_full_name = officer_discord_id__officer_full_name[
                                discord_id_for_user_currently_in_executive_discord_role
                            ]
                        logger.info(
                            "[about/validate_discord_roles_members.py() ] removing the role "
                            f"{executive_discord_role_name} from user "
                            f"{officer_full_name} with discord profile "
                            f"{user_currently_in_executive_discord_role['user']['username']}("
                            f"{discord_id_for_user_currently_in_executive_discord_role})"
                        )
                    else:
                        # if the user is currently in a role that they don't belong to and have an entry in
                        # the members_id__role_ids dictionary
                        users_current_roles = (
                            members_id__role_ids[discord_id_for_user_currently_in_executive_discord_role]
                        )
                        if executive_discord_role_obj['id'] in users_current_roles:
                            del users_current_roles['roles'][executive_discord_role_obj['id']]
                            username = (
                                officer_discord_id__officer_full_name
                                [discord_id_for_user_currently_in_executive_discord_role]
                            )
                            logger.info(
                                "[about/validate_discord_roles_members.py() ] removing the role "
                                f"{executive_discord_role_name} from user "
                                f"{username} with discord profile "
                                f"{user_currently_in_executive_discord_role['user']['username']}"
                                f"({discord_id_for_user_currently_in_executive_discord_role})"
                            )
            for user_that_should_be_in_discord_role in officers_that_should_be_in_discord_role:
                discord_ids_for_users_currently_in_executive_role = [
                    user['user']['id'] for user in users_currently_in_executive_discord_role
                ]
                if position_is_executive_officer:
                    discord_id_for_users_that_should_be_in_exec_discord_group_role.append(
                        user_that_should_be_in_discord_role.discord_id
                    )
                    user_that_should_have_role_do_not_have_role = (
                        exec_discord_role_id not in
                        user_id__user_obj[user_that_should_be_in_discord_role.discord_id]['roles']
                    )
                    if user_that_should_have_role_do_not_have_role:
                        logger.info(
                            f"[about/validate_discord_roles_members.py() ] adding "
                            f"{user_that_should_be_in_discord_role.full_name} to the list of users that "
                            f"should be in the execs discord role {executive_discord_role_name}"
                        )
                user_not_in_role_but_should_be_in_role = (
                    user_that_should_be_in_discord_role.discord_id not in
                    discord_ids_for_users_currently_in_executive_role
                )
                if user_not_in_role_but_should_be_in_role:
                    if user_that_should_be_in_discord_role.discord_id not in members_id__role_ids:
                        username = (
                            user_id__user_obj[user_that_should_be_in_discord_role.discord_id]['user']['username']
                        )
                        members_id__role_ids[user_that_should_be_in_discord_role.discord_id] = \
                            {
                                "username": username,
                                "roles": user_id__user_obj[user_that_should_be_in_discord_role.discord_id]['roles']
                            }
                    members_id__role_ids[
                        user_that_should_be_in_discord_role.discord_id
                    ]['roles'][executive_discord_role_name] = executive_discord_role_obj['id']
                    logger.info(
                        "[about/validate_discord_roles_members.py() ] add the role "
                        f"{executive_discord_role_name} to user {user_that_should_be_in_discord_role.full_name}"
                    )
