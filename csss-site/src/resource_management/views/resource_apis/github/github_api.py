import logging

import github

logger = logging.getLogger('csss_site')
from github import Github


class GitHubAPI:

    def __init__(self, access_token):
        self.connection_successful = False
        if access_token is None:
            logger.info("access_token is not valid")
            return
        try:
            self.git = Github(access_token)  # https://pygithub.readthedocs.io/en/latest/github.html
            self.org = self.git.get_organization(
                'CSSS')  # https://pygithub.readthedocs.io/en/latest/github_objects/Organization.html#github.Organization.Organization
            self.connection_successful = True
        except Exception as e:
            logger.error(
                f"[Github __init__()] experienced following error when trying to connect to Github and get Org "
                f"\"CSSS\":\n{e}")

    def add_non_officer_to_a_team(self, users, team_name):
        """Add listed users to a specific team

        Keyword Arguments:
        users -- a list of all the users who need to be added to the team
        team_name -- the name of the team to add them to
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
                                f"[Github add_user_to_team()] adding {github_user} to CSSS org and inviting them to {team} team.")
                            self.org.invite_user(user=github_user, teams=[team])
                        elif not team.has_in_members(github_user):
                            logger.info(f"[Github add_user_to_team()] adding {github_user} to the {team} team.")
                            team.add_membership(github_user)
                        else:
                            logger.info(
                                f"[Github add_user_to_team()] it seems that {github_user} already is in the org and a member "
                                f"of the {team} team")
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
            logger.info("reading from org CSSS")

            for user in users_team_membership.keys():
                github_user = self.git.search_users(query=f"user:{user}")
                for team in users_team_membership[user]:
                    git_team = self.org.get_team_by_slug(team)
                    if not git_team.has_in_members(github_user):
                        logger.info(f"[Github add_user_to_team()] adding {github_user} to the {team} team.")
                        team.add_membership(github_user)

            for team in self.org.get_teams():
                for user in team.get_members():
                    if team.name not in users_team_membership[user]:
                        logger.info(f"remove the user {user} from team {team}")
                        team.remove_membership(user)
