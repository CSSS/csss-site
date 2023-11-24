#!/usr/bin/env python
import argparse
import os
import subprocess
from enum import Enum
from pathlib import Path

ENV_FILE_LOCATION = 'CI/validate_and_deploy/2_deploy/csss_site.env'
RUN_ENV_FILE_LOCATION = 'CI/validate_and_deploy/2_deploy/run_csss_site.env'


def write_env_variables(
    DB_TYPE, DB_PASSWORD, DB_NAME, DB_PORT, DB_CONTAINER_NAME,
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS,
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY,
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY,
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY,
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY,
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC, GDRIVE_TOKEN_LOCATION, GITHUB_ACCESS_TOKEN,
    SFU_CSSS_GMAIL_USERNAME, SFU_CSSS_GMAIL_PASSWORD, DISCORD_BOT_TOKEN, GUILD_ID, SFU_ENDPOINT_TOKEN, DEV_DISCORD_ID,
    INSTALL_REQUIREMENTS, SETUP_DATABASE, DOWNLOAD_ANNOUNCEMENTS, DOWNLOAD_ANNOUNCEMENT_ATTACHMENTS,
    SETUP_OFFICER_LIST, SETUP_OFFICER_LIST_IMAGES, LAUNCH_WEBSITE
):
    optional_vars = f"DB_TYPE='{DB_TYPE}'"
    if DB_TYPE == 'postgreSQL':
        optional_vars += f"""
DB_PASSWORD='{DB_PASSWORD}'
DB_NAME='{DB_NAME}'
DB_PORT='{DB_PORT}'
DB_CONTAINER_NAME='{DB_CONTAINER_NAME}'
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


parser = argparse.ArgumentParser(
    prog="CSSS Website Runner",
    description='automates the process of setting up and running the CSSS website'
)
parser.add_argument(
    "--env_file", action='store_true', default=False,
    help=(
        f"Indicator of whether to pull the environment variables from the file {ENV_FILE_LOCATION}. "
        f"Helpful if the script has already been run and created {ENV_FILE_LOCATION}"
    )
)
parser.add_argument(
    "--overwrite_env_file", action='store_true',
    help=(
        f"Indicator to the script that while you are pulling the environment from {ENV_FILE_LOCATION} by using "
        f"--env_file flag, you want to override some of the imported variables"
    )
)
parser.add_argument(
    '--database_type', action='store', default=None, choices=['sqlite3', 'postgreSQL'],
    help='Indicates which database type you want to use'
)
parser.add_argument(
    '--install_requirements', action='store', default=None, choices=['true', 'false'],
    help='script will install the required python modules'
)
parser.add_argument(
    '--setup_database', action='store', default=None, choices=['true', 'false'],
    help='script will setup a fresh database'
)
parser.add_argument(
    '--download_announcements', action='store', default=None, choices=['true', 'false'],
    help="script will download the announcements"
)
parser.add_argument(
    '--download_announcement_attachments', action='store', default=None, choices=['true', 'false'],
    help='script will download any attachments associated with the announcements'
)
parser.add_argument(
    '--setup_officer_list', action='store', default=None, choices=['true', 'false'],
    help="script will setup the page that contains the officer list. Necessary only if you need to work on the "
         "page that lists of the officers"
)
parser.add_argument(
    '--setup_officer_list_images', action='store', default=None, choices=['true', 'false'],
    help="script will download the officer pics for the the page that contains the officer list. "
         "Necessary only if you need to work on the page that lists of the officers"
)
parser.add_argument(
    '--launch_website', action='store', default=None, choices=['true', 'false'],
    help='script will run the website'
)
args = parser.parse_args()


class DatabaseType(Enum):
    sqlite3 = 'sqlite3'
    postgreSQL = 'postgreSQL'


def set_boolean_argument(arg):
    if arg == 'true':
        return 'y'
    elif arg == 'false':
        return 'n'
    return None


# run csss_site.env variables
DB_TYPE = None
if args.database_type == DatabaseType.postgreSQL.value:
    DB_TYPE = DatabaseType.postgreSQL.value
elif args.database_type == DatabaseType.sqlite3.value:
    DB_TYPE = DatabaseType.sqlite3.value
DB_PASSWORD = None
DB_NAME = None
DB_PORT = None
DB_CONTAINER_NAME = None
GDRIVE_TOKEN_LOCATION = None
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS = None
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY = None
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY = None
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY = None
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY = None
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC = None
GITHUB_ACCESS_TOKEN = None
SFU_ENDPOINT_TOKEN = None
SFU_CSSS_GMAIL_USERNAME = None
SFU_CSSS_GMAIL_PASSWORD = None
DISCORD_BOT_TOKEN = None
GUILD_ID = None
DEV_DISCORD_ID = None


# run_csss_site.env variables
INSTALL_REQUIREMENTS = set_boolean_argument(args.install_requirements)
SETUP_DATABASE = set_boolean_argument(args.setup_database)
DOWNLOAD_ANNOUNCEMENTS = set_boolean_argument(args.download_announcements)
DOWNLOAD_ANNOUNCEMENT_ATTACHMENTS = set_boolean_argument(args.download_announcement_attachments)
SETUP_OFFICER_LIST = set_boolean_argument(args.setup_officer_list)
SETUP_OFFICER_LIST_IMAGES = set_boolean_argument(args.setup_officer_list_images)
LAUNCH_WEBSITE = set_boolean_argument(args.launch_website)


def get_mandatory_boolean_environment_variable(key, message, default_value=None, default_yes=True,
                                               command_line_value=None, overwrite=False):
    env_variable = command_line_value if command_line_value is not None else os.environ.get(key, None)
    if env_variable is not None and overwrite is False:
        variable = transform_argument_from_env_file_format_to_interactive_menu_format(env_variable)
    else:
        # if the variable is not specified either in the .env file or in the command-line
        variable = take_user_input(f"{message} [Y/n]" if default_yes else f"{message} [y/N]")
    if variable == '' and default_yes is False:
        variable = 'false'
    return (
        variable == 'y' or variable == '' or
        (default_value is not None and variable == default_value.lower())
    )


def get_optional_environment_variable(key, message, overwrite=False):
    env_variable = os.environ.get(key, None)
    if env_variable is not None and overwrite is False:
        # if the variable was detected in the env file and the user did not request to overwrite it
        variable = None if (env_variable is None or env_variable.lower() == 'none') else env_variable
    else:
        variable = take_user_input(message, env_variable=env_variable, skippable_env_variable=True)
    return None if (variable is None or variable.lower() == 's') else variable


def take_user_input(message, env_variable=None, skippable_env_variable=False):
    if env_variable is not None:
        env_variable = transform_argument_from_env_file_format_to_interactive_menu_format(env_variable)
    if skippable_env_variable:
        message += f" [or press s to skip and use the default value of '{env_variable}']"
    message += "\n"
    user_input = input(message)
    while user_input == "" and skippable_env_variable:
        user_input = input(f"Please enter s if you want to skip and use the value of {env_variable} ")
    return user_input if user_input != "s" else env_variable


def transform_argument_from_env_file_format_to_interactive_menu_format(env_variable):
    if env_variable is None or env_variable.lower() == "none":
        return 'none'
    if env_variable.lower() == "true":
        return 'y'
    if env_variable.lower() == 'false':
        return 'n'
    return env_variable.lower()


overwrite_env_file = False
env_file_is_specified = False
if os.path.exists(ENV_FILE_LOCATION) if args.env_file else False:
    subprocess.getstatusoutput("python3 -m pip install python-dotenv")
    from dotenv import load_dotenv

    dotenv_path = Path(ENV_FILE_LOCATION)
    load_dotenv(dotenv_path=dotenv_path)
    if os.path.exists(RUN_ENV_FILE_LOCATION):
        load_dotenv(dotenv_path=RUN_ENV_FILE_LOCATION)
    overwrite_env_file = args.overwrite_env_file
    env_file_is_specified = True


SETUP_DATABASE = get_mandatory_boolean_environment_variable(
    "SETUP_DATABASE", "Do you you want this script to setup the database?", command_line_value=SETUP_DATABASE,
    overwrite=overwrite_env_file
)
DB_TYPE = get_mandatory_boolean_environment_variable(
    "DB_TYPE",
    "Do you want to use db.sqlite3 for the database? [alternative is a separate service,  "
    "dockerized or not]", default_value=DatabaseType.sqlite3.value, command_line_value=DB_TYPE,
    overwrite=overwrite_env_file
)
DB_TYPE = DatabaseType.sqlite3.value if DB_TYPE else DatabaseType.postgreSQL.value
INSTALL_REQUIREMENTS = get_mandatory_boolean_environment_variable(
    "INSTALL_REQUIREMENTS", "Do you want this script to install the python requirements?",
    command_line_value=INSTALL_REQUIREMENTS, overwrite=overwrite_env_file
)
DOWNLOAD_ANNOUNCEMENTS = get_mandatory_boolean_environment_variable(
    "DOWNLOAD_ANNOUNCEMENTS", "Will you be working on the front-page?", default_yes=False,
    command_line_value=DOWNLOAD_ANNOUNCEMENTS, overwrite=overwrite_env_file
)
DOWNLOAD_ANNOUNCEMENT_ATTACHMENTS = get_mandatory_boolean_environment_variable(
    "DOWNLOAD_ANNOUNCEMENT_ATTACHMENTS", "Do you want the announcement attachments as well?",
    default_yes=False, overwrite=overwrite_env_file
) if DOWNLOAD_ANNOUNCEMENTS else False
SETUP_OFFICER_LIST = get_mandatory_boolean_environment_variable(
    "SETUP_OFFICER_LIST", "Will you be working on the page that contains the list of officers?",
    default_yes=False, command_line_value=SETUP_OFFICER_LIST, overwrite=overwrite_env_file
)
SETUP_OFFICER_LIST_IMAGES = get_mandatory_boolean_environment_variable(
    "SETUP_OFFICER_LIST_IMAGES", "Do you want the officer profile pics as well?", default_yes=False,
    command_line_value=SETUP_OFFICER_LIST_IMAGES, overwrite=overwrite_env_file
) if SETUP_OFFICER_LIST else False
LAUNCH_WEBSITE = get_mandatory_boolean_environment_variable(
    "LAUNCH_WEBSITE", "Do you want this script to launch the website?", command_line_value=LAUNCH_WEBSITE,
    overwrite=overwrite_env_file
)
SFU_CSSS_GMAIL_USERNAME = get_optional_environment_variable(
    "SFU_CSSS_GMAIL_USERNAME", "Please enter the username for the sfucsss gmail account",
    overwrite=overwrite_env_file
)
if SFU_CSSS_GMAIL_USERNAME is not None:
    SFU_CSSS_GMAIL_PASSWORD = get_optional_environment_variable(
        "SFU_CSSS_GMAIL_PASSWORD", "Please enter the password for the sfucsss gmail account",
        overwrite=overwrite_env_file
    )
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS = get_optional_environment_variable(
    "GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS",
    "Please enter the team drive ID for the Google Workspace General Documents",
    overwrite=overwrite_env_file
)
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY = get_optional_environment_variable(
    "GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY",
    "Please enter the team drive folder ID for the Google Workspace Public Gallery",
    overwrite=overwrite_env_file
)
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY = get_optional_environment_variable(
    "GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY",
    "Please enter the team drive ID for the Google Workspace Public Gallery",
    overwrite=overwrite_env_file
)
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY = get_optional_environment_variable(
    "GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY",
    "Please enter the team drive folder ID for the Google Workspace Private Gallery",
    overwrite=overwrite_env_file
)
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY = get_optional_environment_variable(
    "GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY",
    "Please enter the team drive ID for the Google Workspace Private Gallery",
    overwrite=overwrite_env_file
)
GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC = get_optional_environment_variable(
    "GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC",
    "Please enter the team drive folder ID for the Google Workspace Deep Exec folder",
    overwrite=overwrite_env_file
)
GDRIVE_TOKEN_LOCATION = get_optional_environment_variable(
    "GDRIVE_TOKEN_LOCATION", "Please enter the location for the google drive token",
    overwrite=overwrite_env_file
)
GITHUB_ACCESS_TOKEN = get_optional_environment_variable(
    "GITHUB_ACCESS_TOKEN", "Please enter the access token for the github app",
    overwrite=overwrite_env_file
)
DISCORD_BOT_TOKEN = get_optional_environment_variable(
    "DISCORD_BOT_TOKEN", "Please enter the token for the CSSS-WEBSITE discord bot",
    overwrite=overwrite_env_file
)
GUILD_ID = get_optional_environment_variable(
    "GUILD_ID", "Please enter the CSSS discord's guild ID", overwrite=overwrite_env_file
)
SFU_ENDPOINT_TOKEN = get_optional_environment_variable(
    "SFU_ENDPOINT_TOKEN", "Please enter the token for the SFU endpoints", overwrite=overwrite_env_file
)
DEV_DISCORD_ID = get_optional_environment_variable(
    "DEV_DISCORD_ID", "Please enter your discord ID", overwrite=overwrite_env_file
)

if DB_TYPE != DatabaseType.sqlite3.value and DB_TYPE != DatabaseType.postgreSQL.value:
    print(f"unrecognized database type of {DB_TYPE} detected")
    exit(1)

if DB_TYPE == DatabaseType.postgreSQL.value:
    DB_PASSWORD = 'test_password'
    DB_NAME = 'csss_website_db'
    DB_PORT = '5432'
    DB_CONTAINER_NAME = 'csss_website_dev_db'

write_env_variables(
    DB_TYPE, DB_PASSWORD, DB_NAME, DB_PORT, DB_CONTAINER_NAME,
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS,
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY,
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY,
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY,
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY,
    GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC, GDRIVE_TOKEN_LOCATION, GITHUB_ACCESS_TOKEN,
    SFU_CSSS_GMAIL_USERNAME, SFU_CSSS_GMAIL_PASSWORD, DISCORD_BOT_TOKEN, GUILD_ID, SFU_ENDPOINT_TOKEN, DEV_DISCORD_ID,
    INSTALL_REQUIREMENTS, SETUP_DATABASE, DOWNLOAD_ANNOUNCEMENTS, DOWNLOAD_ANNOUNCEMENT_ATTACHMENTS,
    SETUP_OFFICER_LIST, SETUP_OFFICER_LIST_IMAGES, LAUNCH_WEBSITE
)