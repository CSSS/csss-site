from django.core.exceptions import ValidationError
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
    )
    year = models.IntegerField(
        default='2022',
    )

    def __str__(self):
        return f"{self.term} {self.year}"


class Officer(models.Model):

    def validate_unique(self, exclude=None):
        if Officer.objects.filter(
                    position_name=self.position_name, name=self.name,
                    elected_term__term_number=self.elected_term.term_number,
                    start_date=self.start_date).exclude(id=self.id).exists():
            raise ValidationError(
                f"There is already an officer saved for term {self.elected_term.term_number} for officer {self.name} "
                f"and position name {self.position_name} under start_date {self.start_date}"
            )

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(Officer, self).save(*args, **kwargs)

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

class NewOfficer(models.Model):
    discord_id = models.CharField(
        max_length=20
    )
    sfu_computing_id = models.CharField(
        max_length=10
    )
    full_name = models.CharField(
        max_length=100,
        default='NA'
    )
    start_date = models.DateTimeField(
        default=timezone.now
    )
    position_name = models.CharField(
        max_length=300,
        default="President"
    )
    re_use_start_date = models.BooleanField(
        default=True
    )
    overwrite_current_officer = models.BooleanField(
        default=False
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"NewOfficer object for {self.full_name} for {self.position_name} for term {self.term}"
