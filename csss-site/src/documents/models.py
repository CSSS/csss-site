from django.db import models
from django.utils.translation import ugettext_lazy as _


# Create your models here.
class DocumentToPull(models.Model):
    name = models.CharField(
        max_length=140,
        default='Document Name',
    )
    file_name = models.CharField(
        max_length=140,
        default='File Name',
    )
    url = models.CharField(
        max_length=2000,
        default='Document URL',
    )
    file_path = models.CharField(
        max_length=500,
        default='Document File Path',
        primary_key=True
    )

    def __str__(self):
        return self.name


class Repo(models.Model):
    name = models.CharField(
        max_length=50,
        default='',
        help_text=_("Name of repository"),
    )
    url = models.CharField(
        max_length=2000,
        default='',
        help_text=_("URL for repository"),
    )
    absolute_path = models.CharField(
        max_length=2000,
        default='',
        help_text=_("Directory where repository is cloned to"),
        primary_key=True
    )
    static_path = models.CharField(
        max_length=2000,
        default='',
        help_text=_("Directory that will be used for static serving of the media"),
        blank=True
    )

    def __str__(self):
        return self.name


class Event(models.Model):
    event_name = models.CharField(
        max_length=140,
        verbose_name=("Event Type"),
        primary_key=True
    )

    def __str__(self):
        return self.event_name


class Album(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        null=True
    )
    date = models.DateField(
        help_text=_("Date"),
        primary_key=True
    )
    name = models.CharField(
        max_length=1000,
        help_text=_("only relevant if each album has a specific theme"),
        verbose_name=('Name of Album')
    )
    album_thumbnail = models.ForeignKey(
        'Media',
        on_delete=models.CASCADE,
        null=True
    )

    def __str__(self):
        return "{0} {1}".format(self.date, self.name)


class Picture(models.Model):
    # fields that are used only for pictures
    absolute_file_path = models.CharField(
        max_length=1000,
        help_text=_("Location of File on Server"),
        verbose_name=('File Path'),
    )
    static_path = models.CharField(
        max_length=2000,
        help_text=_("Directory that will be used for static serving of the media"),
        primary_key=True
    )

    def __str__(self):
        return self.absolute_file_path


class Video(models.Model):
    youtube_link = models.CharField(
        max_length=500,
        verbose_name=('YouTube Link'),
        default=(''),
        primary_key=True
    )

    def __str__(self):
        return self.youtube_link


class Media(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        null=True
    )
    album_link = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        null=True
    )
    picture = models.ForeignKey(
        Picture,
        on_delete=models.CASCADE,
        null=True
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        null=True
    )

    name = models.CharField(
        max_length=140,
        help_text=_("File name to Display"),
        verbose_name=('Name')
    )

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    media = models.ForeignKey(
        Media,
        on_delete=models.CASCADE
    )
    level = models.BigIntegerField()
    name = models.CharField(
        max_length=200,
    )

    def __str__(self):
        return self.name
