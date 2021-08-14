import markdown
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import datetime


# Create your models here.
from elections.views.Constants import HTML_PASSPHRASE_GET_KEY


class Election(models.Model):
    slug = models.SlugField(max_length=32, unique=True)

    human_friendly_name = models.CharField(
        max_length=32,
        default="NONE"
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

    date = models.DateTimeField(
        _(u'Date to be made Public'),
        default=datetime.now,
    )

    websurvey = models.CharField(
        _("The link that the voters can use to vote on"),
        max_length=300,
        default="NONE",
    )

    def __str__(self):
        return "{}_{}".format(self.date, self.election_type)


class Nominee(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)

    name = models.CharField(max_length=140)

    facebook = models.CharField(
        _(u'Facebook Link'),
        max_length=300
    )
    linkedin = models.CharField(
        _(u'LinkedIn Link'),
        max_length=300
    )
    email = models.CharField(
        _(u'Email Address'),
        max_length=300
    )
    discord = models.CharField(
        _(u'Discord Username'),
        max_length=300
    )

    def __str__(self):
        return f"Nominee {self.name} for Election {self.election}"


class NomineeLink(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)

    nominee = models.ForeignKey(Nominee, null=True, on_delete=models.SET_NULL)

    name = models.CharField(max_length=140)

    passphrase = models.CharField(
        max_length=300,
        unique=True,
        null=True
    )

    @property
    def link(self):
        base_url = f"{settings.HOST_ADDRESS}"
        # this is necessary if the user is testing the site locally and therefore is using the port to access the
        # browser
        if settings.PORT is not None:
            base_url += f":{settings.PORT}"
        base_url += f"{settings.URL_ROOT}elections/create_or_update_via_nominee_links_for_nominee?"
        return f"http://{base_url}{HTML_PASSPHRASE_GET_KEY}={self.passphrase}"

    def __str__(self):
        return f"passphrase for nominee {self.name} for election {self.election}"


class NomineeSpeech(models.Model):
    nominee = models.ForeignKey(Nominee, on_delete=models.CASCADE)

    speech = models.CharField(
        max_length=30000,
        default='NA'
    )

    @property
    def social_media_html(self):
        social_media = None
        barrier_needed = False
        if self.nominee.facebook != "NONE":
            social_media = f'<a href="{self.nominee.facebook}" target="_blank">Facebook Profile</a>'
            barrier_needed = True
        if self.nominee.linkedin != "NONE":
            if barrier_needed:
                social_media += " | "
            else:
                social_media = ""
            social_media += f'<a href="{self.nominee.linkedin}" target="_blank">LinkedIn Profile</a>'
            barrier_needed = True
        if self.nominee.email != "NONE":
            if barrier_needed:
                social_media += " | "
            else:
                social_media = ""
            social_media += f'Email: <a href="mailto:{self.nominee.email}"> {self.nominee.email}</a>'
            barrier_needed = True
        if self.nominee.discord != "NONE":
            if barrier_needed:
                social_media += " | "
            else:
                social_media = ""
            social_media += f'Discord Username: {self.nominee.discord}'
        return "" if social_media is None else "<p> Contact/Social Media: " + social_media + "</p>"

    @property
    def formatted_speech(self):
        return markdown.markdown(
            self.speech, extensions=['sane_lists', 'markdown_link_attr_modifier'],
            extension_configs={
                'markdown_link_attr_modifier': {
                    'new_tab': 'on',
                },
            }
        )

    @property
    def formatted_position_names_html(self):
        return ", ".join([position.position_name for position in self.nomineeposition_set.all()])

    def __str__(self):
        return f"speech for Nominee {self.nominee.name} for Election {self.nominee.election}"


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
        return f"Nominee {self.nominee_speech.nominee.name} for Position {self.position_name} " \
               f"for Election {self.nominee_speech.nominee.election}"
