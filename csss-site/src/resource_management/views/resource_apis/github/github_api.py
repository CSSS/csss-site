import logging
from time import sleep

import github
from github import Github

from github.GithubException import RateLimitExceededException, GithubException

logger = logging.getLogger('csss_site')

CSSS_GITHUB_ORG_NAME = 'CSSS'
CSS_GITHUB_ORG_PRIVACY = 'closed'
github_exception_team_name_not_unique = 422
time_to_wait_due_to_github_rate_limit = 60


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
                    CSSS_GITHUB_ORG_NAME)
                # https://pygithub.readthedocs.io/en/latest/github_objects/Organization.html
                # #github.Organization.Organization
                self.connection_successful = True
            except Exception as e:
                self.error_message = f"experienced following error when trying to" \
                                     f" connect to Github and get Org \"{CSSS_GITHUB_ORG_NAME}\":\n{e}"
                logger.error(f"[GitHubAPI __init__()] {self.error_message}")

    def validate_user(self, user_name):
        """
        determine whether or not the specified user_name exists

        Keyword Argument
        user_name -- the github username to validate

        Return
        bool -- true or false to indicate if the github username exists
        error_message -- None if the github user_name does exist. an error message otherwise
        """
        if not self.connection_successful:
            return False, self.error_message
        while True:
            try:
                github_users = self.git.search_users(query=f"user:{user_name}")
                total_count = github_users.totalCount  # noqa: F841
                return True, None
            except RateLimitExceededException:
                sleep(time_to_wait_due_to_github_rate_limit)
            except Exception as e:
                error_message = f" Unable to find user \"{user_name}\" on Github, please create account at " \
                                f"<a href=\"https://github.com\" target=\"_blank\">github.com</a>"
                logger.error(
                    f"[GitHubAPI validate_user()] {error_message} due to following error\n{e}"
                )
                return False, error_message

    def verify_user_in_org(self, user_name, invite_user=False):
        if not self.connection_successful:
            return False, self.error_message

        try:
            if self.org.has_in_members(self.git.search_users(query=f"user:{user_name}")[0]):
                return True, None
            if invite_user:
                success, error_message = self.invite_user_to_org(user_name)
                if success:
                    return success, error_message
                else:
                    logger.info(
                        f"[GitHubAPI verify_user_in_org()] user {user_name} was not found in the SFU"
                        " CSSS Github Org, invite sent"
                    )
                    return success, f"Could not find user {user_name} in the SF CSSS's Github Org, "+error_message
            else:
                return False, f"Could not find user {user_name} in the SF CSSS's Github Org, "
        except Exception as e:
            error_message = f" Unable to verify that user \"{user_name}\" is on the SFU CSSS Github org"
            logger.error(
                f"[GitHubAPI verify_user_in_org()] {error_message} due to following error\n{e}"
            )
            return False, error_message

    def invite_user_to_org(self, user_name):
        if not self.connection_successful:
            return False, self.error_message
        try:
            github_users = self.git.search_users(query=f"user:{user_name}")
            github_user = github_users[0] if github_users.totalCount > 0 else None
            if self.org.has_in_members(github_user):
                return True, None
            self.org.invite_user(user=github_user)
            logger.info(f"[GitHubAPI verify_user_in_org()] invitation sent to user {user_name}")
            return False, f"check email associated with github account {user_name} to " \
                          f"accept the invite"
        except Exception as e:
            error_message = f"unable to add user \"{user_name}\" to the SFU CSSS Github org"
            logger.error(
                f"[GitHubAPI verify_user_in_org()] {error_message} due to following error\n{e}"
            )
            return False, error_message

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
        successful = False
        while not successful:
            try:
                logger.info(f"[GitHubAPI create_team()] attempting to create team {team_name}")
                self.org.create_team(team_name, privacy=CSS_GITHUB_ORG_PRIVACY)
                logger.info(f"[GitHubAPI create_team()] created team {team_name}")
                successful = True
            except RateLimitExceededException:
                sleep(time_to_wait_due_to_github_rate_limit)
            except github.GithubException as e:
                if e.status != github_exception_team_name_not_unique:  # do not bother with exception about
                    # the team name not being unique
                    error_message = f"Unable to create team {team_name}"
                    logger.error(
                        f"[GitHubAPI create_team()] {error_message} due to following error\n{e}")
                    return False, error_message
                else:
                    logger.info(f"[GitHubAPI create_team()] team {team_name} already exists")
                    successful = True

        # removing csss-admin from the team as it gets automatically added when it creates the team
        while True:
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
                    logger.info(
                        f"[GitHubAPI create_team()] {self.git.get_user().login} removed from team {team_name}"
                    )
                else:
                    logger.info(f"[GitHubAPI create_team()] no members detected under team {team_name}")
                return True, None
            except RateLimitExceededException:
                sleep(time_to_wait_due_to_github_rate_limit)
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
        successful = False
        team = None
        while not successful:
            try:
                team = self.org.get_team_by_slug(team_name)
                successful = True
            except RateLimitExceededException:
                sleep(time_to_wait_due_to_github_rate_limit)
            except github.GithubException as e:
                error_message = f" Unable to find team \"{team_name}\""
                logger.error(
                    f"[GitHubAPI add_users_to_a_team()] {error_message} due to following error\n{e}"
                )
                return False, error_message

        for user in users:
            successful = False
            while not successful:
                try:
                    github_users = self.git.search_users(query=f"user:{user}")
                    if github_users.totalCount == 1:
                        github_user = github_users[0]
                        if github_user not in self.org.get_members():
                            logger.info(
                                f"[GitHubAPI add_users_to_a_team()] adding {user} "
                                f"to {CSSS_GITHUB_ORG_NAME} org and inviting them to {team_name} team."
                            )
                            self.org.invite_user(user=github_user, teams=[team])
                            logger.info(
                                f"[GitHubAPI add_users_to_a_team()] send an invite to the user {user} to ORG"
                                f" {CSSS_GITHUB_ORG_NAME} and team {team_name}"
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
                                f"the org {CSSS_GITHUB_ORG_NAME} and a member of the {team} team"
                            )
                    successful = True
                except RateLimitExceededException:
                    sleep(time_to_wait_due_to_github_rate_limit)
                except Exception as e:
                    error_message = f" Unable to add user \"{user}\" to the team {team_name}"
                    logger.error(
                        f"[GitHubAPI add_users_to_a_team()] {error_message} due to following error\n{e}"
                    )
                    return False, error_message
        return True, None

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

        successful = False
        team = None
        while not successful:
            try:
                logger.info(f"[GitHubAPI remove_users_from_a_team()] attempting to get the team {team_name}")
                team = self.org.get_team_by_slug(team_name)
                logger.info(f"[GitHubAPI remove_users_from_a_team()] got the team {team_name}")
                successful = True
            except RateLimitExceededException:
                sleep(time_to_wait_due_to_github_rate_limit)
            except Exception as e:
                error_message = f"unable to get a team by name {team_name}"
                logger.error(
                    f"[GitHubAPI remove_users_from_a_team()] {error_message} due to error\n{e}")
                return False, error_message

        for user in users:
            logger.info(
                f"[GitHubAPI remove_users_from_a_team()] attempting to remove user {user} from team {team_name}"
            )
            successful = False
            while not successful:
                try:
                    github_users = self.git.search_users(query=f"user:{user}")
                    if github_users.totalCount == 1:
                        github_user = github_users[0]
                        team.remove_membership(github_user)
                        logger.info(
                            f"[GitHubAPI remove_users_from_a_team()] removed user {user} from team {team_name}"
                        )
                    successful = True
                except RateLimitExceededException:
                    sleep(time_to_wait_due_to_github_rate_limit)
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
        successful = False
        while not successful:
            try:
                logger.info(f"[GitHubAPI delete_team()] attempting to delete team {team_name}")
                team = self.org.get_team_by_slug(team_name)
                team.delete()
                logger.info(f"[GitHubAPI delete_team()] team {team_name} successfully deleted")
                successful = True
            except RateLimitExceededException:
                sleep(time_to_wait_due_to_github_rate_limit)
            except github.UnknownObjectException as e:
                logger.error(
                    f"[GitHubAPI delete_team()] unable to delete team {team_name} due to "
                    f"error\n{e}")
                successful = True

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
        while True:
            try:
                logger.info(f"[GitHubAPI rename_team()] attempting to rename team from {old_name} to {new_name}")
                team = self.org.get_team_by_slug(old_name)
                team.edit(new_name)
                return True, None
            except RateLimitExceededException:
                sleep(time_to_wait_due_to_github_rate_limit)
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
        logger.info(f"[GitHubAPI ensure_proper_membership()] reading from org {CSSS_GITHUB_ORG_NAME}")

        for team in users_team_membership['team_names']:
            self.create_team(team)

        for user in users_team_membership.keys():
            if user != 'team_names':
                logger.info(f"[GitHubAPI ensure_proper_membership()] validating access for user {user}")
                github_user = None
                user_has_been_acquired = None
                while user_has_been_acquired is None:
                    try:
                        github_user = self.git.search_users(query=f"user:{user}")[0]
                        user_has_been_acquired = True
                    except RateLimitExceededException:
                        logger.info("[GitHubAPI ensure_proper_membership()] "
                                    f"sleeping for {time_to_wait_due_to_github_rate_limit} seconds since rate "
                                    f"limit was encountered")
                        sleep(time_to_wait_due_to_github_rate_limit)
                    except GithubException as e:
                        logger.error("[GitHubAPI ensure_proper_membership()] "
                                     f"encountered error {e} when looking for user {user}")
                        user_has_been_acquired = False
                if user_has_been_acquired:
                    logger.info("[GitHubAPI ensure_proper_membership()] found github profile "
                                f"{github_user} for user {user}")
                    for team in users_team_membership[user]:
                        successful = False
                        while not successful:
                            try:
                                git_team = self.org.get_team_by_slug(team)
                                if not git_team.has_in_members(github_user):
                                    logger.info("[Github ensure_proper_membership()] adding "
                                                f"{github_user} to the {team} team.")
                                    git_team.add_membership(github_user)
                                successful = True
                            except RateLimitExceededException:
                                sleep(time_to_wait_due_to_github_rate_limit)
                            except Exception as e:
                                successful = True
                                logger.error(
                                    "[GitHubAPI ensure_proper_membership()] encountered following error when trying "
                                    f"to add the user {user} to team {team}\n{e}"
                                )
                else:
                    logger.error("[GitHubAPI ensure_proper_membership()] could not find the "
                                 f"github profile for user {user}")

        for team in self.org.get_teams():
            successful = False
            while not successful:
                try:
                    team_name = team.name.lower()
                    if team_name not in users_team_membership['team_names']:
                        git_team = self.org.get_team_by_slug(team_name)
                        git_team.delete()
                        logger.info(
                            f"[GitHubAPI ensure_proper_membership()] deleted team {team_name} since it's not"
                            f" in the list of team_names : {users_team_membership['team_names']}"
                        )
                    else:
                        logger.info(f"[GitHubAPI ensure_proper_membership()] validating memberships in team {team}")
                        for user in team.get_members():
                            user_name = user.login.lower()
                            logger.info("[GitHubAPI ensure_proper_membership()] validating "
                                        f"{user_name}'s memberships in team {team}")
                            if user_name not in users_team_membership:
                                logger.info(
                                    f"[GitHubAPI ensure_proper_membership()] could not find user {user_name} "
                                    f"in the users_team_membership dict"
                                )
                            else:
                                logger.info(
                                    f"[GitHubAPI ensure_proper_membership()] users_team_membership[{user_name}]: "
                                    f"{users_team_membership[user_name]}"
                                )
                            if user_name not in users_team_membership or \
                                    team_name not in users_team_membership[user_name]:
                                team.remove_membership(user)
                                logger.info("[GitHubAPI ensure_proper_membership()] removed the user "
                                            f"{user_name} from team {team}")
                    successful = True
                except RateLimitExceededException:
                    sleep(time_to_wait_due_to_github_rate_limit)
