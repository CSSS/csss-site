from django.db import models
import datetime
from django.utils.translation import ugettext_lazy as _

from about.models import Officer


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
    position = models.CharField(
        max_length=300,
        default='President',
    )
    term_position_number = models.IntegerField(
        default=0,
    )

    link = models.CharField(
        max_length=300
    )
    used = models.BooleanField(
        default=False,
    )


class GoogleMailAccountCredentials(models.Model):
    username = models.CharField(
        max_length=300
    )
    password = models.CharField(
        max_length=300
    )


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


class OfficerGithubTeamMapping(models.Model):
    position = models.CharField(
        max_length=300,
        default='President',
    )
    team_name = models.CharField(
        max_length=300,
        default='officers',
    )


class OfficerGithubTeam(models.Model):
    team_name = models.CharField(
        max_length=5000
    )
    officer = models.ForeignKey(
        Officer,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.officer.name} {self.team_name}"


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


class NaughtyOfficer(models.Model):
    name = models.CharField(
        max_length=300
    )


class NonOfficerMaillistMember(models.Model):
    maillist_name = models.CharField(
        max_length=5000,
    )
    sfuid = models.CharField(
        max_length=5000
    )
