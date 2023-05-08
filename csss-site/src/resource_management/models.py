from django.db import models
from django.utils import timezone

from about.models import OfficerEmailListAndPositionMapping
from csss.PSTDateTimeField import PSTDateTimeField


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
    file_path = models.CharField(
        max_length=5000
    )
    parent_folder_link = models.CharField(
        max_length=5000
    )
    file_owner = models.CharField(
        max_length=5000
    )
    number_of_nags = models.IntegerField(
        default=0
    )
    latest_date_check = PSTDateTimeField(
        default=timezone.now
    )

    def __str__(self):
        return f"{self.file_name} owned by {self.file_owner}"


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
    latest_date_check = PSTDateTimeField(
        default=timezone.now
    )

    def __str__(self):
        return f"{self.user} invalid access to root Google Drive"


class GoogleDriveNonMediaFileType(models.Model):
    mime_type = models.CharField(
        max_length=500
    )
    file_extension = models.CharField(
        max_length=500,
        blank=True,
    )
    note = models.CharField(
        max_length=500
    )

    def __str__(self):
        return f"tracking file type {self.mime_type} with note {self.note}"


class MediaToBeMoved(models.Model):
    file_name = models.CharField(
        max_length=500
    )
    file_path = models.CharField(
        max_length=5000
    )
    parent_folder_link = models.CharField(
        max_length=1000
    )

    def __str__(self):
        return f"Media to Move: {self.file_name}"
