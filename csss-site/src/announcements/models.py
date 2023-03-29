from django.db import models
from django_mailbox.models import Message
from django_markdown.models import MarkdownField

from about.models import Term


class ManualAnnouncement(models.Model):
    title = models.CharField(
        max_length=32,
        default=None,
        unique=True
    )
    author = models.CharField(
        max_length=32,
        default=None
    )
    slug = models.SlugField(
        max_length=32,
        default=None,
        unique=True
    )
    old_content = MarkdownField(
        default=None,
        null=True
    )
    content = models.CharField(
        max_length=3000,
        default=None,
        null=True
    )
    date = models.DateTimeField()

    def __str__(self):
        return self.title


class Announcement(models.Model):
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='relevant_announcements',
        default=None
    )
    email = models.ForeignKey(
        Message,
        related_name='visibility_indicator',
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True
    )
    manual_announcement = models.ForeignKey(
        ManualAnnouncement,
        related_name='visibility_indicator',
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True
    )
    date = models.DateTimeField()

    author = models.CharField(
        max_length=200,
        default=None,
        blank=True
    )

    display = models.BooleanField(
        default=None,
        blank=True
    )

    def __str__(self):
        if self.email is None:
            return f"{self.manual_announcement}"
        else:
            return f"{self.email}"
