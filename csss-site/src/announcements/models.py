from django.db import models
from django_mailbox.models import Message


class Post(models.Model):
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
    content = models.CharField(
        max_length=5000,
        default=None
    )
    processed = models.DateTimeField()

    def __str__(self):
        return self.title


class PostsAndEmails(models.Model):
    email = models.ForeignKey(
        Message,
        related_name='visibility_indicator',
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post,
        related_name='visibility_indicator',
        on_delete=models.CASCADE
    )
    page_number = models.IntegerField(
        default=0
    )
    show = models.BooleanField()