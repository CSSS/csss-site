import json
from time import sleep

import requests
from django.conf import settings

from csss.settings import discord_header
from csss.setup_logger import Loggers
from csss.views_helper import determine_if_specified_term_obj_is_for_current_term

EXEC_DISCORD_ROLE_NAME = 'Execs'


def assign_discord_roles(discord_role_name, discord_recipient_id, term_obj, role_is_executive_officer=False):
    """
    Assigns any necessary discord roles to the new officer

    Keyword Argument
    discord_role_name -- the name of the Officer specific role to assign to the new Officer
    discord_recipient_id -- the discord ID of the new officer
    term_obj -- the term that the officer has been elected for
    role_is_executive_officer -- indicates if the officer has to be assigned the exec group role as well

    Return
    bool -- True or false depending on if there was an issue with talking to the discord API
    error_message -- the message received alongside the error
    """
    if determine_if_specified_term_obj_is_for_current_term(term_obj) and settings.GUILD_ID is not None:
        discord_role_names = [discord_role_name]
        if role_is_executive_officer:
            discord_role_names.append(EXEC_DISCORD_ROLE_NAME)
        success, error_message, matching_roles = get_discord_guild_roles(discord_role_names)
        if not success:
            return success, error_message
        exec_discord_role_id = matching_roles[EXEC_DISCORD_ROLE_NAME]['id'] \
            if (role_is_executive_officer and EXEC_DISCORD_ROLE_NAME in matching_roles) else None
        officer_discord_role_id = matching_roles[discord_role_name]['id'] \
            if discord_role_name in matching_roles else None
        if role_is_executive_officer and exec_discord_role_id is None:
            return False, f"Could not find the discord role \"{EXEC_DISCORD_ROLE_NAME}\""
        if officer_discord_role_id is None:
            return False, f"Could not find the discord roles \"{discord_role_name}\""

        success, error_message, discord_recipient_roles = get_discord_roles_for_specific_user(discord_recipient_id)
        if not success:
            return success, error_message
        discord_recipient_roles.append(officer_discord_role_id)
        if role_is_executive_officer:
            discord_recipient_roles.append(exec_discord_role_id)
        return assign_roles_to_officer(discord_recipient_id, discord_recipient_roles)
    return True, None


def get_discord_roles_for_specific_user(discord_recipient_id):
    """
    Gets the current discord roles for the specified discord user

    Keyword Argument
    discord_recipient_id -- the discord ID for the user whose roles are needed

    Return
    bool -- true or false depending on if the roles were retrievable
    error_message -- the error message if the roles were not retrievable. or None
    roles -- the list of roles that were retrieved if a success, or None
    """
    guild_member = requests.get(
        f"https://discord.com/api/guilds/{settings.GUILD_ID}/members/{discord_recipient_id}",
        headers=discord_header
    )
    if guild_member.status_code != 200:
        return False, f"Unable to interact with Discord API due to error \"{guild_member.reason}\"", None
    return True, None, json.loads(guild_member.content)['roles']


def get_discord_guild_roles(discord_role_names):
    """
    Gets the list of roles in the discord guild

    Keyword Arguments
    discord_role_name -- the names that the calling function is interested in

    Return
    bool -- true or false if able ot get the discord roles for the guild
    error_message -- the error message if the roles were not retrievable, or None
    roles -- a map where the key is the role name and the value is the role object, or None
    """
    roles = requests.get(
        f"https://discord.com/api/guilds/{settings.GUILD_ID}/roles",
        headers=discord_header
    )
    if roles.status_code != 200:
        return False, f"Unable to interact with Discord API due to error \"{roles.reason}\"", None
    return True, None, {
        role['name']: role for role in json.loads(roles.text)
        if role['name'] in discord_role_names
    }


def assign_roles_to_officer(discord_id_of_new_officer_with_role, discord_role_ids):
    """
    Assigns the specified discord roles to the specified discord user

    Keyword Argument
    discord_id_of_new_officer_with_role -- the discord id of the new officer whose roles have to be updated on discord
    discord_role_ids - the list of discord role IDs that have to be assigned to the new officer

    Return
    bool -- true or false if the roles for the specified officer's discord user profile was updated
    error_message -- the error message if the roles could not be assigned to the user, or None
    """
    logger = Loggers.get_logger()
    url = f"https://discord.com/api/guilds/{settings.GUILD_ID}/members/{discord_id_of_new_officer_with_role}"
    discord_role_ids = list(set(discord_role_ids))  # if there are any duplicate IDs in this, it results
    # in the dumbest and most vague error response to walk this earth
    body = {'roles': discord_role_ids}
    logger.info(
        f"[about/assign_discord_roles.py() assign_roles_to_officer() ] calling url={url} with body {body}"
    )
    retry = True
    response = None
    while retry:
        response = requests.patch(
            url,
            headers=discord_header,
            json=body
        )
        if response.status_code == 429:
            retry_after = response.headers.get("retry_after", None)
            if retry_after is None:
                retry_after = response.headers.get("Retry-After", None)
            if retry_after is not None:
                logger.debug(
                    f"[about/assign_discord_roles.py() assign_roles_to_officer()] sleeping for {retry_after}"
                )
                sleep(retry_after)
                retry = True
            else:
                logger.error(
                    f"[about/assign_discord_roles.py() assign_roles_to_officer()] no retry after header found in"
                    f"{response.headers}"
                )
                return False, "Encountered a rate limit without any retry after specified in the header"
        else:
            retry = False
    if response.status_code not in [200, 204]:
        return False, (
            f"Unable to assign discord role due to reason '{response.reason}' with "
            f"an error message of '{json.loads(response.text)['message']}'"
        )
    return True, None
