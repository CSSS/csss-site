#!/usr/bin/env python
import argparse
import os
import subprocess
from enum import Enum
from pathlib import Path

ENV_FILE_LOCATION = 'CI/validate_and_deploy/2_deploy/csss_site.env'
RUN_ENV_FILE_LOCATION = 'CI/validate_and_deploy/2_deploy/run_csss_site.env'


class DatabaseType(Enum):
    sqlite3 = 'sqlite3'
    postgreSQL = 'postgreSQL'


def create_argument_parser():
    """

    :return: an argparser
    """
    parser_obj = argparse.ArgumentParser(
        prog="CSSS Website Runner",
        description='automates the process of setting up and running the CSSS website'
    )
    parser_obj.add_argument(
        "--env_file", action='store_true', default=False,
        help=(
            f"Indicator of whether to pull the environment variables from the file {ENV_FILE_LOCATION}. "
            f"Helpful if the script has already been run and created {ENV_FILE_LOCATION}"
        )
    )
    parser_obj.add_argument(
        "--overwrite_env_file", action='store_true',
        help=(
            f"Indicator to the script that while you are pulling the environment from {ENV_FILE_LOCATION} by using "
            f"--env_file flag, you want to override some of the imported variables"
        )
    )
    parser_obj.add_argument(
        '--database_type', action='store', default=None,
        choices=[DatabaseType.sqlite3.value, DatabaseType.postgreSQL.value],
        help='Indicates which database type you want to use'
    )
    parser_obj.add_argument(
        '--install_requirements', action='store', default=None, choices=['true', 'false'],
        help='script will install the required python modules'
    )
    parser_obj.add_argument(
        '--setup_database', action='store', default=None, choices=['true', 'false'],
        help='script will setup a fresh database'
    )
    parser_obj.add_argument(
        '--download_announcements', action='store', default=None, choices=['true', 'false'],
        help="script will download the announcements"
    )
    parser_obj.add_argument(
        '--download_announcement_attachments', action='store', default=None, choices=['true', 'false'],
        help='script will download any attachments associated with the announcements'
    )
    parser_obj.add_argument(
        '--setup_officer_list', action='store', default=None, choices=['true', 'false'],
        help="script will setup the page that contains the officer list. Necessary only if you need to work on the "
             "page that lists of the officers"
    )
    parser_obj.add_argument(
        '--setup_officer_list_images', action='store', default=None, choices=['true', 'false'],
        help="script will download the officer pics for the the page that contains the officer list. "
             "Necessary only if you need to work on the page that lists of the officers"
    )
    parser_obj.add_argument(
        '--launch_website', action='store', default=None, choices=['true', 'false'],
        help='script will run the website'
    )
    return parser_obj


def convert_command_line_argument_to_menu_format(arg):
    """
    Converts the command-line boolean value into the same format as the menu takes in from the user
    :param arg:
    :return:
    """
    if arg == 'true':
        return 'y'
    elif arg == 'false':
        return 'n'
    return None


def pull_variable_from_command_line_arguments(argparser):
    """

    :param argparser: the argparse object
    :return: (
        the database type command-line flag
        the install_requirements command-line flag
        the setup_database command-line flag
        the download_announcements command-line flag
        the download_announcement_attachments command-line flag
        the setup_officer_list command-line flag
        the setup_officer_list_images command-line flag
        the launch_website command-line flag
    )
    """
    database_type = None
    if argparser.database_type == DatabaseType.sqlite3.value:
        database_type = DatabaseType.sqlite3.value
    elif argparser.database_type == DatabaseType.postgreSQL.value:
        database_type = DatabaseType.postgreSQL.value
    return (
        database_type, convert_command_line_argument_to_menu_format(argparser.install_requirements),
        convert_command_line_argument_to_menu_format(argparser.setup_database),
        convert_command_line_argument_to_menu_format(argparser.download_announcements),
        convert_command_line_argument_to_menu_format(argparser.download_announcement_attachments),
        convert_command_line_argument_to_menu_format(argparser.setup_officer_list),
        convert_command_line_argument_to_menu_format(argparser.setup_officer_list_images),
        convert_command_line_argument_to_menu_format(argparser.launch_website),

    )


def import_env_variables_from_env_file():
    """

    :return: overwrite_env_file -- the overwrite_env_file command-line flag indicating if the user wants to
     overwrite any env variables from the env file
    """
    overwrite_env_file = False
    if os.path.exists(ENV_FILE_LOCATION) if args.env_file else False:
        subprocess.getstatusoutput("python3 -m pip install python-dotenv")
        from dotenv import load_dotenv

        dotenv_path = Path(ENV_FILE_LOCATION)
        load_dotenv(dotenv_path=dotenv_path)
        if os.path.exists(RUN_ENV_FILE_LOCATION):
            load_dotenv(dotenv_path=RUN_ENV_FILE_LOCATION)
        overwrite_env_file = args.overwrite_env_file
    return overwrite_env_file


def check_for_null_variables(**kwargs):
    """
    Indicator of whether any of the variables in the dict are None
    :param kwargs: a dictionary of the necessary keys
    :return: True, key if any of the necessary Keys are None and False, None otherwise
    """
    for key, value in kwargs.items():
        if value is None:
            return True, key
    return False, None


def get_boolean_variable(message, variable_name, description=None, command_line_argument=None, overwrite_env=False,
                         default_is_yes=True):
    """

    :param message: the message for the variable when taking in the user's input
    :param variable_name: the key for the variable in the environment
    :param description: the description for the message when taking in the user's input
    :param command_line_argument: the command-line argument that the user may have set
    :param overwrite_env: indicator of whether the user has requested to overwrite the env variable that was detected
     in the .env file
    :param default_is_yes: indicates if the default boolean is a Yes or No if the user chooses to skip
    :return: Boolean
    """
    if command_line_argument is not None:
        # user specified the variable in the command-line so no need to ask the user anything
        if command_line_argument.lower() == 'y':
            return True
        elif command_line_argument.lower() == 'n':
            return False
    variable = os.environ.get(variable_name, None)
    default_value = 'y' if default_is_yes else 'n'
    if variable is None:
        # if the variable could not be detected on the command-line or via the environment
        # [which means it wasn't in the env files] then the user has to be asked
        variable = take_user_input_for_boolean_variable(
            variable_name, message, description=description, default_value=default_value,
            default_is_yes=default_is_yes, is_default_value=True
        )
    else:
        variable = 'y' if variable.lower() == 'true' else 'n'  # necessary since the environment variable that
        # is pulled from the env file is either 'True' or 'False'
        if overwrite_env:
            # if the variable was in the environment but the user requested to the option of overriding it
            variable = take_user_input_for_boolean_variable(
                variable_name, message, description=description, default_value=variable, default_is_yes=default_is_yes,
                is_default_value=variable == default_value
            )
    return variable == 'y'


def take_user_input_for_boolean_variable(variable_name, message, description=None, default_value=None,
                                         default_is_yes=True, is_default_value=False):
    """

    :param variable_name: the key for the variable in the environment
    :param message: the message for the variable when taking in the user's input
    :param description: the description for the message when taking in the user's input
    :param default_value: the default value to use if the user chooses to skip answering the variable
    :param default_is_yes: indicates if the default boolean is a Yes or No if the user chooses to skip
    :return: y/n string
    """
    message = f"\n{message}"
    message += "\nOptions for answer: " + ("Y/n" if default_is_yes else "y/N")
    choices = ['y', 'n']
    if choices is None:
        raise Exception(f"no choices detected for variable {variable_name}")
    if default_value is not None:
        choices.append("s")
        message += (
            f"\n[or press s to skip and revert to the {'default ' if is_default_value else ''}"
            f"value of '{default_value}']"
        )
    if description is not None:
        message += f"\n{description}"
    message += "\n"
    user_input = input(message).lower()
    while user_input not in choices:
        user_input = input("Please try again\n").lower()
    if user_input == 's':
        user_input = default_value
    return user_input


def get_string_variables(message, variable_name, description=None, command_line_argument=None, overwrite_env=False,
                         default_value=None, choices=None, nullable_variable=False):
    """

    :param message: the message for the variable when taking in the user's input
    :param variable_name: the key for the variable in the environment
    :param description: the description for the message when taking in the user's input
    :param command_line_argument: the command-line argument that the user may have set
    :param overwrite_env: indicator of whether the user has requested to overwrite the env variable that was detected
     in the .env file
    :param default_value: the default string value to use of the variable
    :param choices: the choices that a user can select from for a variable, if it's not an open-ended string variable
    :return: the string for the environment variable
    """
    if command_line_argument is not None:
        # user specified the variable in the command-line so no need to ask the user anything
        return command_line_argument
    variable = os.environ.get(variable_name, None)
    if variable is None:
        variable = take_user_input_for_string_variable(
            message, description=description, default_value=default_value, choices=choices, is_default_value=True,
            nullable_variable=nullable_variable
        )
    elif overwrite_env:
        is_default_value = (variable.lower() == 'none' and default_value is None) or (variable == default_value)
        variable = take_user_input_for_string_variable(
            message, description=description, default_value=variable, choices=choices,
            is_default_value=is_default_value, nullable_variable=nullable_variable
        )
    return variable


def take_user_input_for_string_variable(message, description=None, default_value=None, choices=None,
                                        is_default_value=False, nullable_variable=False):
    """

    :param message: the message for the variable when taking in the user's input
    :param description: the description for the message when taking in the user's input
    :param default_value: the default string value to use of the variable
    :param choices: the choices that a user can select from for a variable, if it's not an open-ended string variable
    :return: the string for the environment variable
    """
    message = f"\n{message}"
    if choices is not None:
        message += "\nOptions for answer: " + ", ".join(choices)
    if default_value is not None:
        if choices is not None:
            choices.append("s")
        message += (
            f"\n[or press s to skip and revert to the {'default ' if is_default_value else ''}"
            f"value of '{default_value}']"
        )
    elif nullable_variable:
        message += (
            f"\n[or press s to skip and revert to the {'default ' if is_default_value else ''}"
            f"value of '{default_value}']"
        )
    if description is not None:
        message += f"\n{description}"
    message += "\n"
    user_input = input(message).strip()
    if choices is not None:
        lower_case_choices = [choice.lower() for choice in choices]
        while user_input.lower() not in lower_case_choices:
            user_input = input("Please try again\n").strip()
    else:
        if nullable_variable:
            while user_input == '':
                # doing the only error checking that
                # can be done with an open-ended string variable where no default value is specified
                user_input = input("Please try again\n").strip()
        else:
            while (user_input.lower() == 's' or user_input == '') and default_value is None:
                # doing the only error checking that
                # can be done with an open-ended string variable where no default value is specified
                user_input = input("Please try again\n").strip()
    if user_input.lower() == "s":
        user_input = 'none' if (default_value is None and nullable_variable) else default_value
    if user_input.lower() == 'none' and nullable_variable:
        user_input = None
    return user_input


parser = create_argument_parser()
args = parser.parse_args()

(
    DB_TYPE_CMD_LINE_ARGUMENT, INSTALL_REQUIREMENTS_CMD_LINE_ARGUMENT, SETUP_DATABASE_CMD_LINE_ARGUMENT,
    DOWNLOAD_ANNOUNCEMENTS_CMD_LINE_ARGUMENT, DOWNLOAD_ANNOUNCEMENT_ATTACHMENTS_CMD_LINE_ARGUMENT,
    SETUP_OFFICER_LIST_CMD_LINE_ARGUMENT, SETUP_OFFICER_LIST_IMAGES_CMD_LINE_ARGUMENT,
    LAUNCH_WEBSITE_CMD_LINE_ARGUMENT
) = pull_variable_from_command_line_arguments(args)

overwrite_env_file = import_env_variables_from_env_file()

SETUP_DATABASE = get_boolean_variable(
    "Do you you want this script to setup the database?", "SETUP_DATABASE",
    command_line_argument=SETUP_DATABASE_CMD_LINE_ARGUMENT, overwrite_env=overwrite_env_file
)
DB_TYPE = get_string_variables(
    "What database do you want to use?", "DB_TYPE", command_line_argument=DB_TYPE_CMD_LINE_ARGUMENT,
    overwrite_env=overwrite_env_file, default_value=DatabaseType.sqlite3.value,
    choices=[DatabaseType.sqlite3.value, DatabaseType.postgreSQL.value]
)
INSTALL_REQUIREMENTS = get_boolean_variable(
    "Do you want this script to install the python requirements?", "INSTALL_REQUIREMENTS",
    command_line_argument=INSTALL_REQUIREMENTS_CMD_LINE_ARGUMENT, overwrite_env=overwrite_env_file
)
DOWNLOAD_ANNOUNCEMENTS = get_boolean_variable(
    "Will you be working on the front-page?", "DOWNLOAD_ANNOUNCEMENTS",
    command_line_argument=DOWNLOAD_ANNOUNCEMENTS_CMD_LINE_ARGUMENT, overwrite_env=overwrite_env_file,
    default_is_yes=False
)
DOWNLOAD_ANNOUNCEMENT_ATTACHMENTS = get_boolean_variable(
    "Do you want the announcement attachments as well?", "DOWNLOAD_ANNOUNCEMENT_ATTACHMENTS",
    command_line_argument=DOWNLOAD_ANNOUNCEMENT_ATTACHMENTS_CMD_LINE_ARGUMENT, overwrite_env=overwrite_env_file,
    default_is_yes=False
) if DOWNLOAD_ANNOUNCEMENTS else False
SETUP_OFFICER_LIST = get_boolean_variable(
    "Will you be working on the page that contains the list of officers?", "SETUP_OFFICER_LIST",
    command_line_argument=SETUP_OFFICER_LIST_CMD_LINE_ARGUMENT, overwrite_env=overwrite_env_file,
    default_is_yes=False
)
SETUP_OFFICER_LIST_IMAGES = get_boolean_variable(
    "Do you want the officer profile pics as well?", "SETUP_OFFICER_LIST_IMAGES",
    command_line_argument=SETUP_OFFICER_LIST_IMAGES_CMD_LINE_ARGUMENT, overwrite_env=overwrite_env_file,
    default_is_yes=False
) if SETUP_OFFICER_LIST else False

LAUNCH_WEBSITE = get_boolean_variable(
    "Do you want this script to launch the website?", "LAUNCH_WEBSITE",
    command_line_argument=LAUNCH_WEBSITE_CMD_LINE_ARGUMENT, overwrite_env=overwrite_env_file
)
SFU_CSSS_GMAIL_USERNAME = get_string_variables(
    "Please enter the username for the sfucsss gmail account", "SFU_CSSS_GMAIL_USERNAME",
    overwrite_env=overwrite_env_file, nullable_variable=True
)
SFU_CSSS_GMAIL_PASSWORD = get_string_variables(
    "Please enter the password for the sfucsss gmail account", "SFU_CSSS_GMAIL_PASSWORD",
    overwrite_env=overwrite_env_file, nullable_variable=True
) if SFU_CSSS_GMAIL_USERNAME is not None else None
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS = get_string_variables(
    "Please enter the team drive ID for the Google Workspace General Documents",
    "GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS",
    overwrite_env=overwrite_env_file, nullable_variable=True
)
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY = get_string_variables(
    "Please enter the team drive folder ID for the Google Workspace Public Gallery",
    "GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY",
    overwrite_env=overwrite_env_file, nullable_variable=True
)
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY = get_string_variables(
    "Please enter the team drive ID for the Google Workspace Public Gallery",
    "GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY",
    overwrite_env=overwrite_env_file, nullable_variable=True
)
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY = get_string_variables(
    "Please enter the team drive folder ID for the Google Workspace Private Gallery",
    "GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY",
    overwrite_env=overwrite_env_file, nullable_variable=True
)
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY = get_string_variables(
    "Please enter the team drive ID for the Google Workspace Private Gallery",
    "GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY",
    overwrite_env=overwrite_env_file, nullable_variable=True
)
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC = get_string_variables(
    "Please enter the team drive folder ID for the Google Workspace Deep Exec folder",
    "GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC",
    overwrite_env=overwrite_env_file, nullable_variable=True
)
GDRIVE_TOKEN_LOCATION = get_string_variables(
    "Please enter the location for the google drive token", "GDRIVE_TOKEN_LOCATION",
    overwrite_env=overwrite_env_file, nullable_variable=True
)
GITHUB_ACCESS_TOKEN = get_string_variables(
    "Please enter the access token for the github app", "GITHUB_ACCESS_TOKEN",
    overwrite_env=overwrite_env_file, nullable_variable=True
)
DISCORD_BOT_TOKEN = get_string_variables(
    "Please enter the token for the CSSS-WEBSITE discord bot", "DISCORD_BOT_TOKEN",
    overwrite_env=overwrite_env_file, nullable_variable=True
)
GUILD_ID = get_string_variables(
    "Please enter the CSSS discord's guild ID", "GUILD_ID", overwrite_env=overwrite_env_file, nullable_variable=True
)
SFU_ENDPOINT_TOKEN = get_string_variables(
    "Please enter the token for the SFU endpoints", "SFU_ENDPOINT_TOKEN", overwrite_env=overwrite_env_file,
    nullable_variable=True
)
DEV_DISCORD_ID = get_string_variables(
    "Please enter your discord ID", "DEV_DISCORD_ID", overwrite_env=overwrite_env_file, nullable_variable=True
)


optional_vars = f"DB_TYPE='{DB_TYPE}'"
if DB_TYPE == DatabaseType.postgreSQL.value:
    optional_vars += f"""
DB_PASSWORD='test_password'
DB_NAME='csss_website_db'
DB_PORT='5432'
DB_CONTAINER_NAME='csss_website_dev_db'
"""
with open(ENV_FILE_LOCATION, "w") as f:
    f.seek(0)
    f.write(f"""ENVIRONMENT='LOCALHOST'
DEBUG='True'
{optional_vars}

GDRIVE_TOKEN_LOCATION='{GDRIVE_TOKEN_LOCATION}'
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS='{GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS}'
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY='{GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY}'
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY='{GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY}'
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY='{GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY}'
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY='{GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY}'
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC='{GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC}'

GITHUB_ACCESS_TOKEN='{GITHUB_ACCESS_TOKEN}'

SFU_ENDPOINT_TOKEN='{SFU_ENDPOINT_TOKEN}'

SFU_CSSS_GMAIL_USERNAME='{SFU_CSSS_GMAIL_USERNAME}'
SFU_CSSS_GMAIL_PASSWORD='{SFU_CSSS_GMAIL_PASSWORD}'

DISCORD_BOT_TOKEN='{DISCORD_BOT_TOKEN}'
GUILD_ID='{GUILD_ID}'
DEV_DISCORD_ID='{DEV_DISCORD_ID}'""")

with open(RUN_ENV_FILE_LOCATION, "w") as f:
    f.seek(0)
    f.write(f"""HELP_SELECTED='0'
INSTALL_REQUIREMENTS='{INSTALL_REQUIREMENTS}'
SETUP_DATABASE='{SETUP_DATABASE}'
DOWNLOAD_ANNOUNCEMENTS='{DOWNLOAD_ANNOUNCEMENTS}'
DOWNLOAD_ANNOUNCEMENT_ATTACHMENTS='{DOWNLOAD_ANNOUNCEMENT_ATTACHMENTS}'
SETUP_OFFICER_LIST='{SETUP_OFFICER_LIST}'
SETUP_OFFICER_LIST_IMAGES='{SETUP_OFFICER_LIST_IMAGES}'
LAUNCH_WEBSITE='{LAUNCH_WEBSITE}'""")
