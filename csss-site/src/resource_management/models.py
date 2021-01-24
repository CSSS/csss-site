from django.db import models
import datetime

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from about.models import OfficerEmailListAndPositionMapping


class ProcessNewOfficer(models.Model):
    passphrase = models.CharField(
        max_length=300,
        primary_key=True,
    )
    term_choices = (
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
        ('Fall', 'Fall'),
    )
    term = models.CharField(
        max_length=6,
        choices=term_choices,
        default='Fall',
        help_text=_("You need to click on the dropbox above in order for the slug field to get populated"),
    )

    year = models.IntegerField(
        choices=[(b, b) for b in list(reversed(range(1970, datetime.datetime.now().year + 1)))],
        default='2018',
        help_text=_("You need to click on the dropbox above in order for the slug field to get populated"),
    )
    position_name = models.CharField(
        max_length=300,
        default='President',
    )
    position_index = models.IntegerField(
        default=0,
    )

    link = models.CharField(
        max_length=300
    )
    used = models.BooleanField(
        default=False,
    )

    start_date = models.DateTimeField(
        default=timezone.now
    )

    new_start_date = models.BooleanField(
        default=True
    )

    sfu_officer_mailing_list_email = models.CharField(
        max_length=140,
        default="NA"
    )

    def __str__(self):
        return f"Processing object for new officer {self.position_name} for term {self.year} {self.term}"


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

    def __str__(self):
        return f"officer position mapping for {self.officer_position_mapping} to" \
               f" github team {self.github_team.team_name}"


class GoogleMailAccountCredentials(models.Model):
    username = models.CharField(
        max_length=300
    )
    password = models.CharField(
        max_length=300
    )

    def __str__(self):
        return f"credentials for gmail {self.username}"


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


class NaughtyOfficer(models.Model):
    sfuid = models.CharField(
        max_length=300,
        default="NA"
    )

    def __str__(self):
        return f"Naughty Officer {self.sfuid}"