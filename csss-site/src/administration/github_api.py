

class GitHub:

    def __init__(self, access_token):
        if access_token is None:
            print("access_token is not valid")
            return
        try:
            self.git = Github(access_token)
            self.org = self.git.get_organization('CSSS')
        except Exception as e:
            print(f"[Github __init__()] experienced following error when trying to connect to Github and get Org \"CSSS\":\n{e}")

    def add_users_to_a_team(self, users, team_id):
        """Add listed users to a specific team

        Keyword Arguments:
        users -- a list of all the users who need to be added to the team
        team_id -- the id of the team to add them to
        """
        team = self.org.get_team(team_id)
        for user in users:
            github_user = self.git.get_user(user)
            if github_user not in self.org.get_members():
                print(f"[Github add_user_to_team()] adding {github_user} to CSSS org and inviting them to {team} team.")
                self.org.invite_user(user=github_user,teams=team)
            elif not team.has_in_members(github_user):
                print(f"[Github add_user_to_team()] adding {github_user} to the {team} team".)
                team.add_membership(github_user)
            else:
                print(f"[Github add_user_to_team()] it seems that {github_user} already is in the org and a member of the {team} team")

    def remove_users_from_a_team(self, users, team_id):
        """Remove listed users from a specific team

        Keyword Arguments:
        users -- a list of all the users who need to be removed from a team
        team_id -- the id of the team they need to be removed from
        """
        team = self.org.get_team(team_id)
        for user in users:
            github_user = self.git.get_user(user)
            team.remove_membership(user)

    def ensure_proper_membership(self,users_team_membership):
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
        for user in users_team_membership:
            github_user = self.git.get_user(user)
            for team in user['teams']:
                if not team.has_in_members(github_user):
                    print(f"[Github add_user_to_team()] adding {github_user} to the {team} team".)

        for team in self.org.get_teams():
            for user in team.get_members():
                if team.id not in users_team_membership[user]:
                    team.remove_membership(user)
