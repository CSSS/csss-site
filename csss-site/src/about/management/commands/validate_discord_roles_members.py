import json
import logging

import requests
from django.conf import settings
from django.core.management import BaseCommand

from about.models import Officer, OfficerEmailListAndPositionMapping
from about.views.input_new_officers.enter_new_officer_info.grant_digital_resource_access.assign_discord_roles import \
    EXEC_DISCORD_ROLE_NAME, get_discord_guild_roles
from csss.settings import discord_header
from csss.views_helper import get_current_term_obj

logger = logging.getLogger('csss_site')


class Command(BaseCommand):
    help = "Ensure that the Discord Roles associated with the Officers have valid members"

    def handle(self, *args, **options):

        current_officers = Officer.objects.all().filter(elected_term=get_current_term_obj())
        position_infos = OfficerEmailListAndPositionMapping.objects.all()

        success, error_message, user_in_roles, user_id_map = get_all_users()
        if not success:
            return success, error_message
        discord_role_names = [
            position_info.discord_role_name
            for position_info in position_infos
        ]
        discord_role_names.append(EXEC_DISCORD_ROLE_NAME)
        success, error_message, matching_executive_roles = get_discord_guild_roles(discord_role_names)
        if not success:
            return success, error_message

        exec_discord_role_id = matching_executive_roles[EXEC_DISCORD_ROLE_NAME]['id'] \
            if EXEC_DISCORD_ROLE_NAME in matching_executive_roles else None

        del matching_executive_roles[EXEC_DISCORD_ROLE_NAME]

        members_id__role_ids = {}  # current officer
        discord_id_for_users_that_should_be_in_exec_discord_group_role = []
        determine_changes_for_position_specific_discord_role_validation(
            user_id_map, user_in_roles, members_id__role_ids,
            discord_id_for_users_that_should_be_in_exec_discord_group_role, position_infos,
            matching_executive_roles, current_officers
        )
        determine_changes_for_exec_discord_group_role_validation(
            user_id_map, user_in_roles, members_id__role_ids,
            discord_id_for_users_that_should_be_in_exec_discord_group_role, exec_discord_role_id
        )

        logger.info(
            "[about/validate_discord_roles_members.py() Command() ] final permission change of "
            f"{json.dumps(members_id__role_ids, indent=3)}"
        )
        # for discord_id, roles in members_id__role_ids.items():
        #     assign_roles_to_officer(discord_id, roles)


def get_all_users():
    """
    Creates a map where of the roles and the members that are a part of them

    Return
    bool -- True or false depending on if there was an issue with talking to the discord API
    error_message -- the message received alongside the error
    user_in_roles -- a dictionary where the key is the discord_role_id and the value is a
     list of the users in that role
    user_id_map -- a dictionary where the key is the discord user id and the value is the
     corresponding user object
    """
    user_in_roles = {}
    after = None
    first = True
    user_id_map = {}
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
                    user_id_map[user['user']['id']] = user
                    for role_id in user['roles']:
                        if role_id in user_in_roles:
                            user_in_roles[role_id].append(user)
                        else:
                            user_in_roles[role_id] = [user]
                after = users[len(users) - 1]['user']['id']
            else:
                after = None
        else:
            return False, f"Unable to get the users with the following url [{base_url}]", user_in_roles, user_id_map
    return True, None, user_in_roles, user_id_map


def determine_changes_for_position_specific_discord_role_validation(
    user_id_map, user_in_roles, members_id__role_ids, discord_id_for_users_that_should_be_in_exec_discord_group_role,
        position_infos, matching_executive_roles, current_officers):
    """
    Populates members_id__role_ids, discord_id_for_users_that_should_be_in_exec_discord_group_role
    with the dictionary where the key is the discord user id and the value is the list of roles they need to have
    and the list of discord user IDS of users who have to be in the Execs discord group role respectively

    Keyword Arguments
    user_id_map -- a dictionary where the key is the discord user id and the value is the
     corresponding user object
    user_in_roles -- a dictionary where the key is the discord_role_id and the value is a
     list of the users in that role
    members_id__role_ids -- the dict that will be updated with all users who have to have their roles updates
     to either remove an exec-associated discord role or assign them with a exec-associated discord dole
    discord_id_for_users_that_should_be_in_exec_discord_group_role -- a list that will be populated with the list
     of discord IDs for the users who have to be the ones in the Execs discord group role
    position_infos -- queryset of all the current position mappings
    matching_executive_roles -- a map where the key is the role name and the value is the role object
    current_officers -- a queryset of officers in the current term

    """
    for (matching_executive_discord_role_name, matching_executive_discord_role) in matching_executive_roles.items():
        positions_that_map_to_the_discord_role = position_infos.filter(
            discord_role_name=matching_executive_discord_role_name
        )
        executive_officer = positions_that_map_to_the_discord_role.first().executive_officer
        positions_that_map_to_the_discord_role = list(
            positions_that_map_to_the_discord_role.values_list('position_name', flat=True)
        )
        officers_that_should_be_in_discord_role = current_officers.filter(
            position_name__in=positions_that_map_to_the_discord_role
        )
        users_in_executive_role = user_in_roles[matching_executive_discord_role['id']]
        for user_in_executive_role in users_in_executive_role:
            user_in_executive_role_id = user_in_executive_role['user']['id']
            list_of_officer_ids_that_belong_to_discord_role = list(
                officers_that_should_be_in_discord_role.values_list('discord_id', flat=True)
            )
            if user_in_executive_role_id not in list_of_officer_ids_that_belong_to_discord_role:
                if user_in_executive_role_id not in members_id__role_ids:
                    user_in_executive_role['roles'].remove(matching_executive_discord_role['id'])
                    members_id__role_ids[user_in_executive_role_id] = user_in_executive_role['roles']
                    logger.info(
                        "[about/validate_discord_roles_members.py() ] removing the role "
                        f"{matching_executive_discord_role_name} from user {user_in_executive_role_id}"
                    )
                else:
                    if matching_executive_discord_role['id'] in members_id__role_ids[user_in_executive_role_id]:
                        members_id__role_ids[user_in_executive_role_id].remove(
                            matching_executive_discord_role['id']
                        )
                        logger.info(
                            "[about/validate_discord_roles_members.py() ] removing the role "
                            f"{matching_executive_discord_role_name} from user {user_in_executive_role_id}"
                        )
        for user_that_should_be_in_discord_role in officers_that_should_be_in_discord_role:
            discord_ids_for_users_in_executive_role = [user['user']['id'] for user in users_in_executive_role]
            if executive_officer:
                discord_id_for_users_that_should_be_in_exec_discord_group_role.append(
                    user_that_should_be_in_discord_role.discord_id
                )
                logger.info(
                    "[about/validate_discord_roles_members.py() ] add the role "
                    f"adding {user_that_should_be_in_discord_role.full_name} to the list of users"
                    f"that should be in the execs discord group role"
                )
            if user_that_should_be_in_discord_role.discord_id not in discord_ids_for_users_in_executive_role:
                if user_that_should_be_in_discord_role.discord_id not in members_id__role_ids:
                    members_id__role_ids[user_that_should_be_in_discord_role.discord_id] = \
                        user_id_map[user_that_should_be_in_discord_role.discord_id]['roles']
                members_id__role_ids[user_that_should_be_in_discord_role.discord_id].append(
                    discord_ids_for_users_in_executive_role
                )
                logger.info(
                    "[about/validate_discord_roles_members.py() ] add the role "
                    f"{matching_executive_discord_role_name} to user {user_that_should_be_in_discord_role.full_name}"
                )


def determine_changes_for_exec_discord_group_role_validation(
    user_id_map, user_in_roles, members_id__role_ids, discord_id_for_users_that_should_be_in_exec_discord_group_role,
        exec_discord_role_id):
    """
    Populates/Updates members_id__role_ids to reflect the changes needed to ensure only the current officers have
     the Execs discord group role

    Keyword Arguments
    user_id_map -- a dictionary where the key is the discord user id and the value is the
     corresponding user object
    user_in_roles -- a dictionary where the key is the discord_role_id and the value is a
     list of the users in that role
    members_id__role_ids -- the dict that will be updated with all users who have to have their roles updates
     to either remove an exec-associated discord role or assign them with a exec-associated discord dole
    discord_id_for_users_that_should_be_in_exec_discord_group_role -- a list of all the discord user IDs that have
     to have the Execs discord group role
    exec_discord_role_id -- the role id for the discord Execs role
    """
    users_in_executive_role = user_in_roles[exec_discord_role_id]
    for user_in_executive_role in users_in_executive_role:
        user_in_executive_role_id = user_in_executive_role['user']['id']
        if user_in_executive_role_id not in discord_id_for_users_that_should_be_in_exec_discord_group_role:
            if user_in_executive_role_id not in members_id__role_ids:
                user_in_executive_role['roles'].remove(exec_discord_role_id)
                members_id__role_ids[user_in_executive_role_id] = user_in_executive_role['roles']
                logger.info(
                    "[about/determine_changes_for_exec_discord_group_role_validation.py() ] removing role "
                    f"{exec_discord_role_id} from user {user_in_executive_role_id}"
                )
            else:
                if exec_discord_role_id in members_id__role_ids[user_in_executive_role_id]:
                    members_id__role_ids[user_in_executive_role_id].remove(exec_discord_role_id)
                    logger.info(
                        "[about/determine_changes_for_exec_discord_group_role_validation.py() ] removing role "
                        f"{exec_discord_role_id} from user {user_in_executive_role_id}"
                    )
    for user_that_should_be_in_discord_role in discord_id_for_users_that_should_be_in_exec_discord_group_role:
        discord_ids_for_users_in_executive_role = [user['user']['id'] for user in users_in_executive_role]
        if user_that_should_be_in_discord_role not in discord_ids_for_users_in_executive_role:
            if user_that_should_be_in_discord_role not in members_id__role_ids:
                members_id__role_ids[user_that_should_be_in_discord_role] = \
                    user_id_map[user_that_should_be_in_discord_role]['roles']
            members_id__role_ids[user_that_should_be_in_discord_role].append(exec_discord_role_id)
            logger.info(
                "[about/determine_changes_for_exec_discord_group_role_validation.py() ] add role "
                f"{exec_discord_role_id} to user {user_that_should_be_in_discord_role}"
            )
