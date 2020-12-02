from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import datetime
# Create your models here.


class NominationPage(models.Model):
    class Meta:
        verbose_name_plural = "NominationPages"

    slug = models.SlugField(
        max_length=32,
    )
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
        max_length=16,
        choices=election_type_choices,
        default='General Election',
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
    nomination_page = models.ForeignKey(NominationPage, on_delete=models.CASCADE)

    name = models.CharField(max_length=140)

    officer_position = models.CharField(
        max_length=40,
        default='NA',
    )

    position_name = models.IntegerField(
        default=0
    )

    speech = models.CharField(
        max_length=10000
    )
    facebook = models.CharField(
        _(u'Facebook Link'),
        max_length=300
    )
    linked_in = models.CharField(
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
        return self.name
