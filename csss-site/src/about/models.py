import datetime
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Term(models.Model):
    term_number = models.IntegerField(
        primary_key=True,
        default=0,
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

    def __str__(self):
        return f"{self.term} {self.year}"


class Officer(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['position_name', 'name', 'elected_term__term_number', 'start_date'],
                name="unique_officer_for_term"
            )
        ]

    position_name = models.CharField(
        max_length=300,
        default='President',
    )

    position_index = models.IntegerField(
        default=0,
    )
    name = models.CharField(
        max_length=140,
        default="NA"
    )

    start_date = models.DateTimeField(
        default=timezone.now
    )

    sfuid = models.CharField(
        max_length=140,
        default="NA"
    )

    sfu_email_alias = models.CharField(
        max_length=140,
        default="NA"
    )

    phone_number = models.BigIntegerField(
        default=0
    )

    github_username = models.CharField(
        max_length=140,
        default="NA"
    )

    gmail = models.CharField(
        max_length=140,
        default="NA"
    )

    course1 = models.CharField(
        _(u'First Favorite Course'),
        max_length=100,
        default="NA"
    )

    course2 = models.CharField(
        _(u'Second Favorite Course'),
        max_length=100,
        default="NA"
    )

    language1 = models.CharField(
        _(u'First Favorite Language'),
        max_length=100,
        default="NA"
    )

    language2 = models.CharField(
        _(u'Second Favorite Language'),
        max_length=100,
        default="NA"
    )

    bio = models.CharField(
        max_length=2000,
        default="NA"
    )

    image = models.CharField(
        _(u'Link to Profile Picture'),
        max_length=400,
        default='NA'
    )

    elected_term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
    )
    sfu_officer_mailing_list_email = models.CharField(
        max_length=140,
        default="NA"
    )

    def __str__(self):
        return f" {self.elected_term} {self.name}"


class AnnouncementEmailAddress(models.Model):
    email = models.CharField(
        max_length=140,
        default="NA"
    )
    officer = models.ForeignKey(
        Officer,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.officer.name} {self.email} {self.officer.elected_term}"


class OfficerEmailListAndPositionMapping(models.Model):
    position_index = models.IntegerField(
        default=0,
    )
    position_name = models.CharField(
        max_length=300,
        default="President"
    )
    email = models.CharField(
        max_length=140,
        default="NA"
    )

    marked_for_deletion = models.BooleanField(
        default=False
    )

    elected_via_election_officer = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"OfficerEmailListAndPositionMapping: {self.position_index}, {self.position_name}, {self.email}"
