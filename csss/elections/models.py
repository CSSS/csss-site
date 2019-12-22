from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import datetime
# Create your models here.

class NominationPage(models.Model):
    class Meta:
        verbose_name_plural = "NominationPages"

    slug = models.SlugField(
        max_length=32,
        unique=True,
        help_text = _("This field will be pre-populated using the below two fields."),
    )

    type_of_elections_choices = (
        ('General_Election', 'General Election'),
        ('By_Election', 'By-Election'),
    )

    type_of_election = models.CharField(
        max_length=16,
        choices=type_of_elections_choices,
        default='General',
        help_text = _("You need to click on the dropbox above in order for the slug field to get populated"),
    )

    slugDate = models.DateField(
		_(u'Date to be used to create the slug field'),
        default=datetime.now,
        help_text = _("This field will be used to populate the slug field"),
    )

    datePublic = models.DateTimeField(
        _(u'Date to be made Public'),
        default=datetime.now,
    )

    websurvey = models.CharField(
        _("The link that the voters can use to vote on"),
        max_length = 300,
        default="NONE",
        help_text = _("It is necessary to prefix the link with \"http[s]://\"")
    )

    def __str__(self):
        return str(self.slugDate) +"_"+ self.type_of_election

class Nominee(models.Model):
	nominationPage = models.ForeignKey(NominationPage, on_delete=models.CASCADE)
	name = models.CharField(max_length=140)

	Position = models.CharField(
		max_length=40,
		default='NA',
	)
	Speech = models.CharField(max_length=2000)
	Facebook = models.CharField(_(u'Facebook Link'),max_length=300)
	LinkedIn = models.CharField(_(u'LinkedIn Link'),max_length=300)
	Email = models.CharField(_(u'Email Address'),max_length=300)
	Discord_Username = models.CharField(_(u'Discord Username'),max_length=300)

	def __str__(self):
		return self.name
