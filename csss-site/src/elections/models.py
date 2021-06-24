from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import datetime


# Create your models here.

class Election(models.Model):
    slug = models.SlugField(max_length=32, unique=True)

    human_friendly_name = models.CharField(
        max_length=32,
        default="NONE"
    )
    election_type_choices = (
        ('general_election', 'General Election'),
        ('by_election', 'By-Election'),
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

    def __str__(self):
        return f"passphrase for nominee {self.name} for election {self.election}"


class NomineeSpeech(models.Model):
    nominee = models.ForeignKey(Nominee, on_delete=models.CASCADE)

    speech = models.CharField(
        max_length=30000,
        default='NA'
    )

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
