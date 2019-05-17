from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class DocumentToPull(models.Model):
    name=models.CharField(
        max_length=140,
        default='Document Name',
    )
    fileName = models.CharField(
        max_length=140,
        default='File Name',
    )
    url=models.CharField(
        max_length=2000,
        default='Document URL',
    )
    filePath=models.CharField(
        max_length=500,
        default='Document File Path',
    )

    def __str__(self):
        return self.name

class Repo(models.Model):
    name=models.CharField(
    max_length=50,
    default='',
    help_text = _("Name of repository"),
    )
    url=models.CharField(
    max_length=2000,
    default='',
    help_text = _("URL for repository"),
    )
    absolute_path=models.CharField(
    max_length=2000,
    default='',
    help_text = _("Directory where repository is cloned to"),
    )
    static_path=models.CharField(
    max_length=2000,
    default='',
    help_text = _("Directory that will be used for static serving of the media"),
    )
    def __str__(self):
        return self.name

class Event(models.Model):
    event_name=models.CharField(
    max_length=140,
    verbose_name=("Event Type")
    )
    def __str__ (self):
        return self.event_name

class Album(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    date=models.DateField(
    help_text = _("Date")
    )
    name=models.CharField(
    max_length=1000,
    help_text = _("only relevant if each album has a specific theme"),
    verbose_name=('Name of Album')
    )
    album_thumbnail = models.ForeignKey('Media', on_delete=models.CASCADE, null=True)
    def __str__(self):
        return "{0} {1}".format(self.date,self.name)

class Media(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    album_link = models.ForeignKey(Album, on_delete=models.CASCADE, null=True)
    name=models.CharField(
    max_length=140,
    help_text = _("File name to Display"),
    verbose_name=('Name')
    )
    absolute_file_path=models.CharField(
    max_length=1000,
    help_text = _("Location of File on Server"),
    verbose_name=('File Path'),
    default=('NA')
    )
    static_path=models.CharField(
    max_length=2000,
    default='',
    help_text = _("Directory that will be used for static serving of the media"),
    )
    pictureType=models.BooleanField(
    help_text = _("True for images and false for links to videos hosted elsewhere"),
    verbose_name=("Media Type"),
    default=True
    )

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    level = models.BigIntegerField()
    name = models.CharField(
    max_length=200,
    )
    def __str__ (self):
        return self.name
