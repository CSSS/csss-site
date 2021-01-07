import logging
from time import sleep

import github
from github import Github
from github.GithubException import RateLimitExceededException, GithubException

from csss.constants import Constants

logger = logging.getLogger('csss_site')


class GitHubAPI:

    def __init__(self, access_token):
        self.connection_successful = False
        self.error_message = None
        if access_token is None:
            self.error_message = "access_token is not valid"
            logger.error(self.error_message)
        else:
            try:
                self.git = Github(access_token)  # https://pygithub.readthedocs.io/en/latest/github.html
                self.org = self.git.get_organization(
                    Constants.CSSS_GITHUB_ORG_NAME)
                # https://pygithub.readthedocs.io/en/latest/github_objects/Organization.html
                # #github.Organization.Organization
                self.connection_successful = True
            except Exception as e:
                self.error_message = f"experienced following error when trying to" \
                                     f" connect to Github and get Org \"{Constants.CSSS_GITHUB_ORG_NAME}\":\n{e}"
                logger.error(f"[GitHubAPI __init__()] {self.error_message}")

    def create_team(self, team_name):
        """
        Will attempt to create the github team with the specified team name

        Keyword Argument
        team_name -- the name to be given to the github team

        Return
        success -- true or false Bool
        error_message -- the error_message if success is False or None otherwise
        """
        if not self.connection_successful:
            return False, self.error_message
        try:
            logger.info(f"[GitHubAPI create_team()] attempting to create team {team_name}")
            self.org.create_team(team_name, privacy=Constants.CSS_GITHUB_ORG_PRIVACY)
            logger.info(f"[GitHubAPI create_team()] created team {team_name}")
        except github.GithubException as e:
            if e.status != Constants.github_exception_team_name_not_unique:  # do not bother with exception about
                # the team name not being unique
                error_message = f"Unable to create team {team_name}"
                logger.error(
                    f"[GitHubAPI create_team()] {error_message} due to following error\n{e}")
                return False, error_message
            else:
                logger.info(f"[GitHubAPI create_team()] team {team_name} already exists")

        # removing csss-admin from the team as it gets automatically added when it creates the team
        try:
            logger.info(
                f"[GitHubAPI create_team()] attempting to remove {self.git.get_user().login} team {team_name}"
            )
            team = self.org.get_team_by_slug(team_name)
            if team.members_count > 0:
                logger.info(
                    f"[GitHubAPI create_team()] the list of users who have membership under team"
                    f" {team_name}: {team.get_members()}"
                )
                github_users = self.git.search_users(query=f"user:{self.git.get_user().login}")
                team.remove_membership(github_users[0])
                logger.info(f"[GitHubAPI create_team()] {self.git.get_user().login} removed from team {team_name}")
            else:
                logger.info(f"[GitHubAPI create_team()] no members detected under team {team_name}")
            return True, None
        except Exception as e:
            error_message = f"Unable to remove the user {self.git.get_user().login} from the team {team_name}"
            logger.error(f"[GitHubAPI create_team()] {error_message} due to following error\n{e}")
            return False, error_message

    def add_users_to_a_team(self, users, team_name):
        """
        Add listed users to a specific team

        Keyword Arguments
        users -- a list of all the users who need to be added to the team
        team_name -- the name of the team to add them to

        return
        success -- true or false Bool
        error_message -- the error_message if success is False or None otherwise
        """
        if not self.connection_successful:
            return False, self.error_message
        try:
            team = self.org.get_team_by_slug(team_name)
        except github.GithubException as e:
            error_message = f" Unable to find team \"{team_name}\""
            logger.error(
                f"[GitHubAPI add_users_to_a_team()] {error_message} due to following error\n{e}"
            )
            return False, error_message

        for user in users:
            github_users = self.git.search_users(query=f"user:{user}")
            try:
                if github_users.totalCount == 1:
                    github_user = github_users[0]
                    if github_user not in self.org.get_members():
                        logger.info(
                            f"[GitHubAPI add_users_to_a_team()] adding {user} "
                            f"to {Constants.CSSS_GITHUB_ORG_NAME} org and inviting them to {team_name} team."
                        )
                        self.org.invite_user(user=github_user, teams=[team])
                        logger.info(
                            f"[GitHubAPI add_users_to_a_team()] send an invite to the user {user} to ORG"
                            f" {Constants.CSSS_GITHUB_ORG_NAME} and team {team_name}"
                        )
                    elif not team.has_in_members(github_user):
                        logger.info(f"[GitHubAPI add_users_to_a_team()] adding {user} to the {team_name} team.")
                        team.add_membership(github_user)
                        logger.info(
                            "[GitHubAPI add_users_to_a_team()] sent an invite to the user"
                            f" {user} for team {team_name}"
                        )
                    else:
                        logger.info(
                            f"[GitHubAPI add_users_to_a_team()] it seems that {github_user} already is in "
                            f"the org {Constants.CSSS_GITHUB_ORG_NAME} and a member of the {team} team"
                        )
            except Exception as e:
                error_message = f" Unable to add user \"{user}\" to the team {team_name}"
                logger.error(
                    f"[GitHubAPI add_users_to_a_team()] {error_message} due to following error\n{e}"
                )
                return False, error_message
        return True, None

    # def verify_team_name_is_valid(self, team_name):
    #     """
    #     Ensuring that the specified team name is valid
    #     """
    #     if not self.connection_successful:
    #         return False, self.error_message
    #     try:
    #         self.org.get_team_by_slug(team_name)
    #         return True
    #     except Exception:
    #         return False

    def remove_users_from_a_team(self, users, team_name):
        """Remove listed users from a specific team

        Keyword Arguments
        users -- a list of all the users who need to be removed from a team
        team_name -- the name of the team they need to be removed from

        return
        success -- true or false Bool
        error_message -- the error_message if success is False or None otherwise
        """
        if not self.connection_successful:
            return False, self.error_message

        try:
            logger.info(f"[GitHubAPI remove_users_from_a_team()] attempting to get the team {team_name}")
            team = self.org.get_team_by_slug(team_name)
            logger.info(f"[GitHubAPI remove_users_from_a_team()] got the team {team_name}")
        except Exception as e:
            error_message = f"unable to get a team by name {team_name}"
            logger.error(
                f"[GitHubAPI remove_users_from_a_team()] {error_message} due to error\n{e}")
            return False, error_message

        for user in users:
            logger.info(
                f"[GitHubAPI remove_users_from_a_team()] attempting to remove user {user} from team {team_name}"
            )
            github_users = self.git.search_users(query=f"user:{user}")
            try:
                if github_users.totalCount == 1:
                    github_user = github_users[0]
                    team.remove_membership(github_user)
                    logger.info(f"[GitHubAPI remove_users_from_a_team()] removed user {user} from team {team_name}")
            except Exception as e:
                error_message = f"unable to remove user {user} from team {team_name}"
                logger.error(f"[GitHubAPI remove_users_from_a_team()] {error_message} due to error\n{e}")
                return False, error_message
        return True, None

    def delete_team(self, team_name):
        """
        deletes the specified team

        Keyword Argument
        team_name -- the name of the team to delete
        """
        if not self.connection_successful:
            return
        try:
            logger.info(f"[GitHubAPI delete_team()] attempting to delete team {team_name}")
            team = self.org.get_team_by_slug(team_name)
            team.delete()
            logger.info(f"[GitHubAPI delete_team()] team {team_name} successfully deleted")
        except github.UnknownObjectException as e:
            logger.error(
                f"[GitHubAPI delete_team()] unable to delete team {team_name} due to "
                f"error\n{e}")

    def rename_team(self, old_name, new_name):
        """
        Renames a github team

        Keyword Arguments
        old_name -- the current name of the github team
        new_name -- the new name of the github team

        Return
        success -- true or false Bool
        error_message -- the error_message if success is False or None otherwise
        """
        if not self.connection_successful:
            return False, None
        try:
            logger.info(f"[GitHubAPI rename_team()] attempting to rename team from {old_name} to {new_name}")
            team = self.org.get_team_by_slug(old_name)
            team.edit(new_name)
            return True, None
        except Exception as e:
            error_message = f"Unable to rename team from {old_name} to {new_name}"
            logger.error(f"[GitHubAPI rename_team()]{error_message} due to following error\n{e}")
            return False, error_message

    def ensure_proper_membership(self, users_team_membership):
        """Ensure that the correct users are in the correct team

        Keyword Arguments:
        users_team_membership -- a dict that lists all the team memberships that need to be set
        Example of users_team_membership
        {
            "user1" : [
                "team1_id", "team2_id", "team3_id"
            ],
            "user2" : [
                "team4_id", "team5_id", "team6_id"
            ],
            "user3" : [
                "team7_id", "team8_id", "team9_id"
            ],
        }
        """
        if not self.connection_successful:
            return False, self.error_message
        logger.info(f"[GitHubAPI ensure_proper_membership()] reading from org {Constants.CSSS_GITHUB_ORG_NAME}")

        for user in users_team_membership.keys():
            logger.info(f"[GitHubAPI ensure_proper_membership()] validating access for user {user}")
            github_users = self.git.search_users(query=f"user:{user}")
            github_user = None
            user_has_been_acquired = None
            while user_has_been_acquired is None:
                try:
                    github_user = github_users[0]
                    user_has_been_acquired = True
                except RateLimitExceededException:
                    logger.info("[GitHubAPI ensure_proper_membership()] "
                                f"sleeping for {Constants.time_to_wait_due_to_github_rate_limit} seconds since rate "
                                f"limit was encountered")
                    sleep(Constants.time_to_wait_due_to_github_rate_limit)
                except GithubException as e:
                    logger.error("[GitHubAPI ensure_proper_membership()] "
                                 f"encountered error {e} when looking for user {user}")
                    user_has_been_acquired = False
            if user_has_been_acquired:
                logger.info("[GitHubAPI ensure_proper_membership()] found github profile "
                            f"{github_user} for user {user}")
                for team in users_team_membership[user]:
                    try:
                        git_team = self.org.get_team_by_slug(team)
                        if not git_team.has_in_members(github_user):
                            logger.info("[Github ensure_proper_membership()] adding "
                                        f"{github_user} to the {team} team.")
                            git_team.add_membership(github_user)
                    except Exception as e:
                        logger.error(
                            "[GitHubAPI ensure_proper_membership()] encountered following error when trying "
                            f"to add the user {user} to team {team}\n{e}"
                        )
            else:
                logger.error("[GitHubAPI ensure_proper_membership()] could not find the "
                             f"github profile for user {user}")

        for team in self.org.get_teams():
            logger.info(f"[GitHubAPI ensure_proper_membership()] validating memberships in team {team}")
            for user in team.get_members():
                logger.info("[GitHubAPI ensure_proper_membership()] validating "
                            f"{user.login}'s memberships in team {team}")
                if user.login.lower() not in users_team_membership or \
                        team.name not in users_team_membership[user.login.lower()]:
                    logger.info("[GitHubAPI ensure_proper_membership()] remove the user "
                                f"{user.login} from team {team}")
                    team.remove_membership(user)
