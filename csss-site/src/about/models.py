import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from csss.PSTDateTimeField import PSTDateTimeField
from csss.convert_markdown import markdown_message


class Term(models.Model):
    term_number = models.IntegerField(
        primary_key=True,
        default=0,
    )

    def save(self, *args, **kwargs):
        self.term_number = self.get_term_number()
        super(Term, self).save(*args, **kwargs)

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
        choices=[(b, b) for b in list(reversed(range(1970, datetime.datetime.now().year + 2)))],
        default='2018',
        help_text=_("You need to click on the dropbox above in order for the slug field to get populated"),
    )

    def get_term_number(self):
        """
        Get the term number for the term

        Return
        term_number -- the term number for the term, or None
        """
        index = 1
        for term_starting_month in Term.term_choices:
            if term_starting_month[0] == self.term:
                if int(index) <= 4:
                    return (self.year * 10) + 1
                elif int(index) <= 8:
                    return (self.year * 10) + 2
                else:
                    return (self.year * 10) + 3
            index += 4
        return None

    def get_term_month_number(self):
        """
        Returns the term month number for the specified term
        """
        for (index, term) in enumerate(Term.term_choices):
            if term[0] == self.term:
                return index + 1

    def __str__(self):
        return f"{self.term} {self.year}"


class Officer(models.Model):

    def validate_unique(self, exclude=None):
        if Officer.objects.filter(
                position_name=self.position_name, full_name=self.full_name,
                elected_term__term_number=self.elected_term.term_number,
                start_date=self.start_date).exclude(id=self.id).exists():
            raise ValidationError(
                f"There is already an officer saved for term {self.elected_term.term_number} for officer "
                f"{self.full_name} and position name {self.position_name} under start_date {self.start_date}"
            )

    def save(self, *args, **kwargs):
        self.validate_unique()
        if hasattr(self, "_bitwarden_is_set"):
            self.bitwarden_is_set = True
            self.bitwarden_takeover_needed = False
        elif not self.bitwarden_is_set:
            self.bitwarden_is_set = True
            position_mapping = OfficerEmailListAndPositionMapping.objects.filter(
                position_name=self.position_name
            ).first()
            if position_mapping is None:
                self.bitwarden_takeover_needed = False
            elif not position_mapping.bitwarden_access:
                self.bitwarden_takeover_needed = False
            else:
                from csss.views_helper import get_previous_term_obj
                last_officer_with_same_position = Officer.objects.all().filter(
                    elected_term__term_number__gte=get_previous_term_obj().term_number,
                    position_name=self.position_name
                ).exclude(id=self.id).order_by('start_date').last()
                if last_officer_with_same_position is not None:
                    if self.start_date == last_officer_with_same_position.start_date:
                        if last_officer_with_same_position.sfu_computing_id == self.sfu_computing_id:
                            # same officer, just continuing in their role so
                            # they dont need to have their password reset
                            self.bitwarden_takeover_needed = False
                        else:
                            # different officer so password has to be reset
                            self.bitwarden_takeover_needed = True
                    else:
                        self.bitwarden_takeover_needed = True
                else:
                    self.bitwarden_takeover_needed = True
        super(Officer, self).save(*args, **kwargs)

    position_name = models.CharField(
        max_length=300,
        default='President',
    )

    position_index = models.IntegerField(
        default=0,
    )
    full_name = models.CharField(
        max_length=140,
        default="NA"
    )

    start_date = PSTDateTimeField(
        default=timezone.now
    )

    sfu_computing_id = models.CharField(
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

    discord_id = models.CharField(
        max_length=200,
        default='NA'
    )

    discord_username = models.CharField(
        max_length=200,
        default='NA'
    )

    discord_nickname = models.CharField(
        max_length=200,
        default='NA'
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

    bitwarden_takeover_needed = models.BooleanField(
        default=True
    )

    bitwarden_is_set = models.BooleanField(
        default=False
    )

    @property
    def get_front_end_start_date(self):
        return datetime.datetime.strftime(self.start_date, "%d %b %Y")

    @property
    def get_front_end_bio(self):
        return markdown_message(self.bio)

    def __str__(self):
        return f" {self.elected_term} {self.full_name}"


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
        return f"{self.officer.full_name} {self.email} {self.officer.elected_term}"


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

    discord_role_name = models.CharField(
        max_length=140,
        default="NA",
    )

    github = models.BooleanField(
        default=True
    )

    google_drive = models.BooleanField(
        default=True
    )

    marked_for_deletion = models.BooleanField(
        default=False
    )

    elected_via_election_officer = models.BooleanField(
        default=False
    )

    executive_officer = models.BooleanField(
        default=True
    )

    election_officer = models.BooleanField(
        default=True
    )

    sfss_council_rep = models.BooleanField(
        default=True
    )

    frosh_week_chair = models.BooleanField(
        default=True
    )

    discord_manager = models.BooleanField(
        default=True
    )

    shared_position = models.BooleanField(
        default=False
    )

    bitwarden_access = models.BooleanField(
        default=True
    )

    number_of_terms_choices = (
        (None, "None"),
        (1, "1"),
        (2, "2"),
        (3, "3"),
    )

    @classmethod
    def number_of_terms_choices_dict(cls, front_end=True):
        return {
            number_of_terms_choice[0 if front_end else 1]: number_of_terms_choice[1 if front_end else 0]
            for number_of_terms_choice in cls.number_of_terms_choices
        }

    @classmethod
    def number_of_terms_choices_to_display_on_html(cls):
        return [
            number_of_terms_choice[1]
            for number_of_terms_choice in cls.number_of_terms_choices
        ]

    number_of_terms = models.IntegerField(
        choices=number_of_terms_choices,
        default=3,
        null=True,
        blank=True
    )

    @property
    def get_number_of_terms(self):
        return str(self.number_of_terms)

    starting_month_choices = (
        (None, "None"),
        (1, 'Spring'),
        (2, 'Summer'),
        (3, 'Fall')
    )

    @classmethod
    def starting_month_choices_to_display_on_html(cls):
        return [
            starting_month_choice[1]
            for starting_month_choice in cls.starting_month_choices
        ]

    @classmethod
    def starting_month_choices_dict(cls, front_end=True):
        return {
            starting_month_choice[0 if front_end else 1]: starting_month_choice[1 if front_end else 0]
            for starting_month_choice in cls.starting_month_choices
        }

    starting_month = models.IntegerField(
        choices=starting_month_choices,
        default=3,
        null=True,
        blank=True
    )

    def get_term_month_number(self):
        return self.starting_month

    @property
    def get_starting_month(self):
        return OfficerEmailListAndPositionMapping.starting_month_choices_dict()[self.starting_month]

    def __str__(self):
        return f"OfficerEmailListAndPositionMapping: {self.position_index}, {self.position_name}, {self.email}"


class UnProcessedOfficer(models.Model):
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
    start_date = PSTDateTimeField(
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

    gmail_verification_code = models.CharField(
        max_length=5,
        unique=True,
        null=True,
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
    )

    number_of_nags = models.IntegerField(
        default=0
    )

    def __str__(self):
        return f"UnProcessedOfficer for {self.full_name} for position {self.position_name} under term {self.term}"
