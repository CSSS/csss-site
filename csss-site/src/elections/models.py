from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from csss.PSTDateTimeField import PSTDateTimeField
from csss.convert_markdown import markdown_message
from csss.views.send_discord_dm import send_discord_dm
from elections.views.Constants import NA_STRING, \
    ENDPOINT_CREATE_OR_UPDATE_NOMINEE_FOR_NOMINEE_VIA_LOGIN__NOMINEE_LINK


class Election(models.Model):
    slug = models.SlugField(max_length=32, unique=True)

    human_friendly_name = models.CharField(
        max_length=32,
        default=None,
        null=True
    )
    election_type_choices = (
        ('general_election', 'General Election'),
        ('by_election', 'By-Election'),
        ('council_rep_election', "Council Rep Election")
    )

    election_type = models.CharField(
        _("Election Type"),
        choices=election_type_choices,
        default='General Election',
        max_length=1000,
    )

    date = PSTDateTimeField(
        _(u'Date to be made Public'),
        default=datetime.now,
    )

    end_date = PSTDateTimeField(
        default=None,
        null=True,
    )

    websurvey = models.CharField(
        _("The link that the voters can use to vote on"),
        max_length=300,
        default=None,
        null=True
    )

    def save(self, *args, **kwargs):
        if self.human_friendly_name is None:
            raise Exception(f"detected a Null value for the name for the election {self}")
        super(Election, self).save(*args, **kwargs)

    def __str__(self):
        return "{}_{}".format(self.date, self.election_type)


class Nominee(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=140)

    @property
    def get_full_name(self):
        return NA_STRING if self.full_name is None else self.full_name

    facebook = models.CharField(
        _(u'Facebook Link'),
        max_length=300,
        default=None,
        null=True
    )

    @property
    def get_facebook(self):
        return NA_STRING if self.facebook is None else self.facebook

    instagram = models.CharField(
        _(u'Instagram Link'),
        max_length=300,
        default=None,
        null=True
    )

    @property
    def get_instagram(self):
        return NA_STRING if self.instagram is None else self.instagram

    linkedin = models.CharField(
        _(u'LinkedIn Link'),
        max_length=300,
        default=None,
        null=True
    )

    @property
    def get_linkedin(self):
        return NA_STRING if self.linkedin is None else self.linkedin

    email = models.CharField(
        _(u'Email Address'),
        max_length=300,
        default=None,
        null=True
    )

    @property
    def get_email(self):
        return NA_STRING if self.email is None else self.email

    discord = models.CharField(
        _(u'Discord Username'),
        max_length=300,
        default=None,
        null=True
    )

    @property
    def get_discord_username(self):
        if self.discord_username is not None:
            return self.discord_username
        if self.discord is not None:
            return self.discord
        return NA_STRING

    discord_id = models.CharField(
        max_length=200,
        default=None,
        null=True
    )

    @property
    def get_discord_id(self):
        return NA_STRING if self.discord_id is None else self.discord_id

    discord_username = models.CharField(
        max_length=200,
        default=None,
        null=True
    )

    discord_nickname = models.CharField(
        max_length=200,
        default=None,
        null=True
    )

    @property
    def get_discord_nickname(self):
        return NA_STRING if self.discord_nickname is None else self.discord_nickname

    sfuid = models.CharField(
        max_length=8,
        default=None,
        null=True
    )

    @property
    def get_sfuid(self):
        return NA_STRING if self.sfuid is None else self.sfuid

    def save(self, *args, **kwargs):
        if 'first_pass' in kwargs:
            first_pass = kwargs['first_pass']
            del kwargs['first_pass']
        else:
            first_pass = True
        # will uncomment below when the SfuID is determined for all past nominees
        # if self.sfuid is None:
        #     raise Exception(
        #         f"detected a Null value for SFUID for the the nominee {self.full_name}"
        #         f"for election {self.election}"
        #     )
        if self.facebook == NA_STRING:
            self.facebook = None
        if self.instagram == NA_STRING:
            self.instagram = None
        if self.linkedin == NA_STRING:
            self.linkedin = None
        if self.email == NA_STRING:
            self.email = None
        if self.discord == NA_STRING:
            self.discord = None
        if self.discord_id == NA_STRING:
            self.discord_id = None
        if self.discord_username == NA_STRING:
            self.discord_username = None
        if self.discord_nickname == NA_STRING:
            self.discord_nickname = None
        if self.sfuid == NA_STRING:
            self.sfuid = None
        super(Nominee, self).save(*args, **kwargs)

        # added to ensure the SFUID is synchronized between the Nominee and their posible NomineeLink object
        nominee_link = self.nomineelink_set.all()
        nominee_link = nominee_link[0] if len(nominee_link) == 1 else None
        if first_pass and nominee_link is not None:
            nominee_link.sfuid = self.sfuid
            nominee_link.discord_id = self.discord_id
            nominee_link.save(first_pass=False)

    def __str__(self):
        return f"Nominee {self.full_name} for Election {self.election}"


class NomineeLink(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)

    nominee = models.ForeignKey(Nominee, null=True, on_delete=models.SET_NULL)

    full_name = models.CharField(max_length=140)

    passphrase = models.CharField(
        max_length=300,
        unique=True,
        null=True
    )

    sfuid = models.CharField(
        max_length=8,
        default=None,
        null=True
    )

    @property
    def get_sfuid(self):
        return NA_STRING if self.sfuid is None else self.sfuid

    discord_id = models.CharField(
        max_length=200,
        default=None,
        null=True
    )

    @property
    def get_discord_id(self):
        return NA_STRING if self.discord_id is None else self.discord_id

    def save(self, *args, **kwargs):
        if 'first_pass' in kwargs:
            first_pass = kwargs['first_pass']
            del kwargs['first_pass']
        else:
            first_pass = True
        if self.full_name == NA_STRING:
            self.full_name = None
        if self.sfuid == NA_STRING:
            self.sfuid = None
        if self.discord_id == NA_STRING:
            self.discord_id = None
        super(NomineeLink, self).save(*args, **kwargs)

        # added to ensure that changes to the NomineeLink's sfuid and discord id propagate to the Nominee object
        if first_pass and self.nominee is not None:
            self.nominee.sfuid = self.sfuid
            self.nominee.discord_id = self.discord_id
            self.nominee.save(first_pass=False)

    def __str__(self):
        return f"Nominee Link for nominee {self.full_name} for election {self.election}"

    def send_dm(self):
        if self.discord_id is not None:
            url = f'http://{settings.HOST_ADDRESS}'
            if settings.DEBUG:
                url += f":{settings.PORT}"
            url += f'/login?next=/elections/{ENDPOINT_CREATE_OR_UPDATE_NOMINEE_FOR_NOMINEE_VIA_LOGIN__NOMINEE_LINK}'

            message = (
                f"Hello {self.full_name},\n\nThanks for being a nominee for the upcoming election. :smiley:\n\n"
                f"[Click on this link to add your your speech to the website]({url})"
                f"\nThe above link need to be filled in for you to be included on the nomination"
            )
            send_discord_dm(
                self.discord_id, f"Fill out CSSS Nominee Information for {self.election.human_friendly_name}",
                message
            )


class NomineeSpeech(models.Model):
    nominee = models.ForeignKey(Nominee, on_delete=models.CASCADE)

    speech = models.CharField(
        max_length=30000,
        default=None,
        null=True
    )

    @property
    def formatted_speech(self):
        return markdown_message(self.speech) if self.speech else ""

    @property
    def speech_for_editing(self):
        return self.format_speech_for_editing(self.speech)

    @staticmethod
    def format_speech_for_editing(speech):
        return speech.replace("`", r'\`')

    @property
    def social_media_html(self):
        social_media = None
        barrier_needed = False
        if self.nominee.facebook is not None:
            social_media = f'<a href="{self.nominee.facebook}" target="_blank">Facebook Profile</a>'
            barrier_needed = True
        if self.nominee.instagram is not None:
            if barrier_needed:
                social_media += " | "
            else:
                social_media = ""
            social_media += f'<a href="{self.nominee.instagram}" target="_blank">Instagram Profile</a>'
            barrier_needed = True
        if self.nominee.linkedin is not None:
            if barrier_needed:
                social_media += " | "
            else:
                social_media = ""
            social_media += f'<a href="{self.nominee.linkedin}" target="_blank">LinkedIn Profile</a>'
            barrier_needed = True
        if self.nominee.email is not None:
            if barrier_needed:
                social_media += " | "
            else:
                social_media = ""
            social_media += f'Email: <a href="mailto:{self.nominee.email}"> {self.nominee.email}</a>'
            barrier_needed = True
        if self.nominee.discord_nickname is not None:
            if barrier_needed:
                social_media += " | "
            else:
                social_media = ""
            social_media += f"Discord Nickname: {self.nominee.discord_nickname}"
        if self.nominee.discord_username is not None:
            if barrier_needed:
                social_media += " | "
            else:
                social_media = ""
            social_media += f"Discord Username: {self.nominee.discord_username}"
        else:
            if self.nominee.discord is not None:
                if barrier_needed:
                    social_media += " | "
                else:
                    social_media = ""
                social_media += f'Discord Username: {self.nominee.discord}'
        return "" if social_media is None else "<p> Contact/Social Media: " + social_media + "</p>"

    @property
    def formatted_position_names_html(self):
        return ", ".join([position.position_name for position in self.nomineeposition_set.all()])

    def __str__(self):
        return f"speech for Nominee {self.nominee.get_full_name} for Election {self.nominee.election}"


class NomineePosition(models.Model):
    nominee_speech = models.ForeignKey(NomineeSpeech, on_delete=models.CASCADE)

    position_name = models.CharField(
        max_length=40,
        default='NA',
    )

    position_index = models.IntegerField(
        default=0,
    )

    def __str__(self):
        return f"Nominee {self.nominee_speech.nominee.full_name} for Position {self.position_name} " \
               f"for Election {self.nominee_speech.nominee.election}"
