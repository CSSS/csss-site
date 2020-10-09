import logging
from time import sleep

import github
from github import Github
from github.GithubException import RateLimitExceededException, GithubException

logger = logging.getLogger('csss_site')


class GitHubAPI:

    def __init__(self, access_token):
        self.connection_successful = False
        self.error_message = None
        if access_token is None:
            self.error_message = "access_token is not valid"
            logger.error(self.error_message)
            return
        try:
            self.git = Github(access_token)  # https://pygithub.readthedocs.io/en/latest/github.html
            self.org = self.git.get_organization(
                'CSSS')
            # https://pygithub.readthedocs.io/en/latest/github_objects/Organization.html
            # #github.Organization.Organization
            self.connection_successful = True
        except Exception as e:
            self.error_message = f"experienced following error when trying to" \
                                 f" connect to Github and get Org \"CSSS\":\n{e}"
            logger.error(f"[Github __init__()] {self.error_message}")

    def add_non_officer_to_a_team(self, users, team_name):
        """
        Add listed users to a specific team

        Keyword Arguments:
        users -- a list of all the users who need to be added to the team
        team_name -- the name of the team to add them to

        return
        success -- true or false Bool
        error_message -- the error_message if success is False or None otherwise
        """
        if self.connection_successful:
            try:
                team = self.org.get_team_by_slug(team_name)
            except github.GithubException as e:
                logger.error(
                    f"[Github add_user_to_team()] Unable to find team \"{team_name}\" due to following error\n{e}"
                )
                return False, f" Unable to find team \"{team_name}\""

            for user in users:
                github_users = self.git.search_users(query=f"user:{user}")
                try:
                    if github_users.totalCount == 1:
                        github_user = github_users[0]
                        if github_user not in self.org.get_members():
                            logger.info(
                                f"[Github add_user_to_team()] adding {github_user} "
                                f"to CSSS org and inviting them to {team} team."
                            )
                            self.org.invite_user(user=github_user, teams=[team])
                        elif not team.has_in_members(github_user):
                            logger.info(f"[Github add_user_to_team()] adding {github_user} to the {team} team.")
                            team.add_membership(github_user)
                        else:
                            logger.info(
                                f"[Github add_user_to_team()] it seems that {github_user} already is in "
                                f"the org and a member of the {team} team"
                            )
                except Exception as e:
                    logger.error(
                        f"[Github add_user_to_team()] Unable to find user \"{user}\" due to following error\n{e}"
                    )
                    return False, f" Unable to find user \"{user}\""
        return True, None

    def remove_users_from_a_team(self, users, team_name):
        """Remove listed users from a specific team

        Keyword Arguments:
        users -- a list of all the users who need to be removed from a team
        team_name -- the name of the team they need to be removed from
        """
        if self.connection_successful:
            team = self.org.get_team_by_slug(team_name)
            for user in users:
                github_users = self.git.search_users(query=f"user:{user}")
                if github_users.totalCount == 1:
                    github_user = github_users[0]
                    team.remove_membership(github_user)

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
        if self.connection_successful:
            logger.info("[GitHubAPI ensure_proper_membership()] reading from org CSSS")

            for user in users_team_membership.keys():
                logger.info(f"[GitHubAPI ensure_proper_membership()] validating access for user {user}")
                github_users = self.git.search_users(query=f"user:{user}")
                github_user = None
                total_count_obtained = False
                error_experienced = False
                while not (total_count_obtained or error_experienced):
                    try:
                        github_user = github_users[0]
                        total_count_obtained = True
                    except RateLimitExceededException:
                        logger.info("[GitHubAPI ensure_proper_membership()] "
                                    "sleeping for 60 seconds since rate limit was encountered")
                        sleep(60)
                    except GithubException as e:
                        logger.error("[GitHubAPI ensure_proper_membership()] "
                                     f"encountered error {e} when looking for user {user}")
                        error_experienced = True
                if not error_experienced:
                    logger.info("[GitHubAPI ensure_proper_membership()] found github profile "
                                f"{github_user} for user {user}")
                    for team in users_team_membership[user]:
                        git_team = self.org.get_team_by_slug(team)
                        if not git_team.has_in_members(github_user):
                            logger.info("[Github ensure_proper_membership()] adding "
                                        f"{github_user} to the {team} team.")
                            git_team.add_membership(github_user)
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
                        logger.info("[Github ensure_proper_membership()] remove the user "
                                    f"{user.login} from team {team}")
                        team.remove_membership(user)
