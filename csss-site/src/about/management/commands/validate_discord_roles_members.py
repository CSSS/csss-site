import json
import logging

import requests
from django.conf import settings
from django.core.management import BaseCommand

from about.models import Officer, OfficerEmailListAndPositionMapping, UnProcessedOfficer
from about.views.input_new_officers.enter_new_officer_info.grant_digital_resource_access.assign_discord_roles import \
    EXEC_DISCORD_ROLE_NAME, get_discord_guild_roles, assign_roles_to_officer
from csss.settings import discord_header
from csss.views_helper import get_current_term_obj

logger = logging.getLogger('csss_site')


class Command(BaseCommand):
    help = "Ensure that the Discord Roles associated with the Officers have valid members"

    def handle(self, *args, **options):

        current_officers = Officer.objects.all().filter(
            elected_term=get_current_term_obj()
        ).exclude(
            sfu_computing_id__in=list(UnProcessedOfficer.objects.all().values_list('sfu_computing_id', flat=True))
        )
        officer_discord_id__officer_full_name = {
            officer.discord_id: officer.full_name for officer in current_officers
        }
        position_infos = OfficerEmailListAndPositionMapping.objects.all()

        success, error_message, role_id__list_of_users, user_id__user_obj = get_all_user_dictionaries()
        if not success:
            logger.info(
                f"[about/validate_discord_roles_members.py() Command() ] {error_message}  "
            )
            return
        success, error_message, role_id__role = get_role_dictionary()
        if not success:
            logger.info(
                f"[about/validate_discord_roles_members.py() Command() ] {error_message}  "
            )
            return
        discord_role_names = [
            position_info.discord_role_name
            for position_info in position_infos
        ]
        discord_role_names.append(EXEC_DISCORD_ROLE_NAME)
        success, error_message, matching_executive_roles = get_discord_guild_roles(discord_role_names)
        if not success:
            logger.info(
                f"[about/validate_discord_roles_members.py() Command() ] {error_message}  "
            )
            return

        exec_discord_role_id = matching_executive_roles[EXEC_DISCORD_ROLE_NAME]['id'] \
            if EXEC_DISCORD_ROLE_NAME in matching_executive_roles else None
        if exec_discord_role_id is None:
            logger.info(
                f"[about/validate_discord_roles_members.py() Command() ] unable to get the role_id for "
                f"the discord group \"{EXEC_DISCORD_ROLE_NAME}\" role"
            )
        else:
            del matching_executive_roles[EXEC_DISCORD_ROLE_NAME]

        members_id__role_ids = {}  # current officer
        discord_id_for_users_that_should_be_in_exec_discord_group_role = []
        determine_changes_for_position_specific_discord_role_validation(
            user_id__user_obj, role_id__list_of_users, role_id__role, officer_discord_id__officer_full_name,
            exec_discord_role_id, members_id__role_ids,
            discord_id_for_users_that_should_be_in_exec_discord_group_role, position_infos,
            matching_executive_roles, current_officers
        )
        determine_changes_for_exec_discord_group_role_validation(
            user_id__user_obj, role_id__list_of_users, role_id__role, members_id__role_ids,
            discord_id_for_users_that_should_be_in_exec_discord_group_role, exec_discord_role_id
        )

        logger.info(
            "[about/validate_discord_roles_members.py() Command() ] final permission change of "
            f"{json.dumps(members_id__role_ids, indent=3)}"
        )
        for discord_id, user_role_info in members_id__role_ids.items():
            success, error_message = assign_roles_to_officer(
                discord_id,
                [role_id for role_name, role_id in user_role_info['roles'].items()]
            )
            if not success:
                logger.info(f"[about/validate_discord_roles_members.py() Command() ] {error_message}")


def get_all_user_dictionaries():
    """
    Creates a dictionary where about the roles and the members that are a part of them

    Return
    bool -- True or false depending on if there was an issue with talking to the discord API
    error_message -- the message received alongside the error
    role_id__list_of_users -- a dictionary where the key is the discord_role_id and the value is a
     list of the users in that role
    user_id__user_obj -- a dictionary where the key is the discord user id and the value is the
     corresponding user object
    """
    role_id__list_of_users = {}
    after = None
    first = True
    user_id__user_obj = {}
    while after is not None or first:
        first = False
        base_url = f"https://discord.com/api/guilds/{settings.GUILD_ID}/members?limit=1000"
        if after is not None:
            url = f"{base_url}&after={after}"
        else:
            url = base_url
        resp = requests.get(url, headers=discord_header)
        if resp.status_code == 200:
            users = json.loads(resp.text)
            if len(users) > 0:
                for user in users:
                    user_id__user_obj[user['user']['id']] = user
                    for role_id in user['roles']:
                        if role_id in role_id__list_of_users:
                            role_id__list_of_users[role_id].append(user)
                        else:
                            role_id__list_of_users[role_id] = [user]
                after = users[len(users) - 1]['user']['id']
            else:
                after = None
        else:
            return (
                False, f"Unable to get the users with the following url [{base_url}]",
                role_id__list_of_users, user_id__user_obj
            )

    return True, None, role_id__list_of_users, user_id__user_obj


def get_role_dictionary():
    """
    Creates a dictionary where the key is the role_id and the value is the role object

    Return
    bool -- True or false depending on if there was an issue with talking to the discord API
    error_message -- the message received alongside the error
    role_id__role -- a dictionary where the key is the role_id and the value is the corresponding role object
    """
    base_url = f"https://discord.com/api/guilds/{settings.GUILD_ID}/roles"
    resp = requests.get(base_url, headers=discord_header)
    role_id__role = None
    if resp.status_code == 200:
        role_id__role = {
            role['id']: role
            for role in json.loads(resp.text)
        }
        return True, None, role_id__role
    else:
        return False, "Unable to get a dictionary of the roles", role_id__role


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
