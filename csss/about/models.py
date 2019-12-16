from django.db import models
from django.utils.translation import ugettext_lazy as _
import datetime

class aboutPage(models.Model):
    title=models.CharField(max_length=140)
    body=models.TextField()

    def __str__(self):
        return self.title
# Create your models here.

class Source_File(models.Model):
    json_file = models.FileField(
        default = 'exec_positions/default',
        upload_to='exec_positions/'
    )

    term_choices = (
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
        ('Fall', 'Fall'),
    )

    term = models.CharField(
        primary_key=True,
        max_length=6,
        choices=term_choices,
        default='Fall',
        help_text = _("You need to click on the dropbox above in order for the slug field to get populated"),
    )

    year = models.IntegerField(
        choices=[ (b,b) for b in list(reversed(range(1970, datetime.datetime.now().year+1))) ],
        default='2018',
        help_text = _("You need to click on the dropbox above in order for the slug field to get populated"),
    )
    def __str__(self):
        return f"{self.year} {self.term}"

class Term(models.Model):
    term_choices = (
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
        ('Fall', 'Fall'),
    )
    term = models.CharField(
        primary_key=True,
        max_length=6,
        choices=term_choices,
        default='Fall',
        help_text = _("You need to click on the dropbox above in order for the slug field to get populated"),
    )
    term_number = models.IntegerField(
        default=0,
    )
    year = models.IntegerField(
        choices=[ (b,b) for b in list(reversed(range(1970, datetime.datetime.now().year+1))) ],
        default='2018',
        help_text = _("You need to click on the dropbox above in order for the slug field to get populated"),
    )

    def __str__(self):
        return f"{self.year} {self.term}"

class Officer(models.Model):

    position = models.CharField(
        max_length=300,
        default='President',
    )

    position_number = models.IntegerField(
        default=0,
    )
    name = models.CharField(
        max_length=140,
        default="NA"
    )

    sfuid = models.CharField(
        max_length=140,
        default="NA"
    )

    phone_number = models.IntegerField(
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
        max_length=10,
        default="NA"
    )

    course2 = models.CharField(
        _(u'Second Favorite Course'),
        max_length=10,
        default="NA"
    )

    language1 = models.CharField(
        _(u'First Favorite Language'),
        max_length=10,
        default="NA"
    )

    language2 = models.CharField(
        _(u'Second Favorite Language'),
        max_length=10,
        default="NA"
    )

    bio = models.CharField(
        max_length=2000,
        default="NA"
    )

    image = models.CharField(_(u'Link to Profile Picture'),max_length=400,default='NA')

    elected_term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


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
