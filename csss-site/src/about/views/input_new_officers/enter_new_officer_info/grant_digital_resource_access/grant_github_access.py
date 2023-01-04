from csss.setup_logger import Loggers
from resource_management.views.resource_apis.github.github_api import GitHubAPI


def grant_github_access(officer_obj, github_teams_to_add):
    """
    Adds a new officer to the github teams they need to be part of

    Keyword Argument
    officer_obj -- the officer that is getting added to the github teams
    github_teams_to_add -- the github teams that the user had to be added to

    Return
    bool -- True or false depending on if there was an issue with talking to the github API
    error_message -- the message received alongside the error
    """
    logger = Loggers.get_logger()
    if len(github_teams_to_add) > 0 and officer_obj.github_username is not None:
        github_api = GitHubAPI()
        if not github_api.connection_successful:
            logger.info("[about/grant_github_access.py grant_github_access()]"
                        f" {github_api.error_message}")
            return False, f"{github_api.error_message}"
        for github_team_to_add in github_teams_to_add:
            success, error_message = github_api.add_users_to_a_team(
                [officer_obj.github_username],
                github_team_to_add.get_team_name()
            )
            if not success:
                logger.info(
                    "[about/grant_github_access.py grant_github_access()] "
                    f"unable to add officer {officer_obj.github_username} to team"
                    f" {github_team_to_add.github_team.team_name} due to error {error_message}"
                )
                return False, error_message
            logger.info(
                "[about/grant_github_access.py grant_github_access()] "
                f"mapped officer {officer_obj} to team {github_team_to_add.github_team.team_name}"
            )
    return True, None
