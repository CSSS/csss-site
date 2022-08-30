from django.db import models

from about.models import OfficerEmailListAndPositionMapping


class OfficerPositionGithubTeam(models.Model):
    team_name = models.CharField(
        max_length=300,
        default='officers',
    )
    marked_for_deletion = models.BooleanField(
        default=False
    )
    relevant_previous_terms = models.IntegerField(
        default=0
    )

    def __str__(self):
        return f"officer github team {self.team_name}"


class OfficerPositionGithubTeamMapping(models.Model):
    github_team = models.ForeignKey(
        OfficerPositionGithubTeam,
        on_delete=models.CASCADE,
        default=None
    )
    officer_position_mapping = models.ForeignKey(
        OfficerEmailListAndPositionMapping,
        on_delete=models.CASCADE
    )

    def get_team_name(self):
        return self.github_team.team_name

    def __str__(self):
        return f"officer position mapping for {self.officer_position_mapping} to" \
               f" github team {self.github_team.team_name}"


class NonOfficerGoogleDriveUser(models.Model):
    gmail = models.CharField(
        max_length=300
    )
    name = models.CharField(
        max_length=300
    )
    file_id = models.CharField(
        max_length=5000
    )

    file_name = models.CharField(
        max_length=5000
    )

    def __str__(self):
        return f"{self.name} access to google drive file {self.file_name}"


class GoogleDrivePublicFile(models.Model):
    file_id = models.CharField(
        max_length=5000
    )
    link = models.CharField(
        max_length=5000
    )
    file_name = models.CharField(
        max_length=5000
    )

    def __str__(self):
        return f"Public Google Drive File {self.file_name}"


class NonOfficerGithubMember(models.Model):
    team_name = models.CharField(
        max_length=5000
    )
    username = models.CharField(
        max_length=5000
    )
    legal_name = models.CharField(
        max_length=140,
        default="NA"
    )

    def __str__(self):
        return f"Non Officer {self.legal_name} access to github team {self.team_name}"


class GoogleDriveFileAwaitingOwnershipChange(models.Model):
    file_id = models.CharField(
        max_length=5000
    )
    file_name = models.CharField(
        max_length=5000
    )
    web_link = models.CharField(
        max_length=5000
    )
    file_owner = models.CharField(
        max_length=5000
    )
    number_of_nags = models.IntegerField(
        default=0
    )
    latest_date_check = models.DateTimeField(

    )

    def __str__(self):
        return f"{self.file_id} owned by {self.file_owner}"


class GoogleDriveRootFolderBadAccess(models.Model):
    file_id = models.CharField(
        max_length=5000
    )
    user = models.CharField(
        max_length=5000
    )
    number_of_nags = models.IntegerField(
        default=0
    )
    latest_date_check = models.DateTimeField(

    )

    def __str__(self):
        return f"{self.user} invalid access to root Google Drive"
