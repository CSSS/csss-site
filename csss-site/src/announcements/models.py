import datetime
import re

from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone
from django_mailbox.models import Message

from about.models import Term
from csss.PSTDateTimeField import PSTDateTimeField
from csss.views.pstdatetime import NewPSTDateTimeField, pstdatetime


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
    content = models.CharField(
        max_length=3000,
        default=None,
        null=True
    )
    date = PSTDateTimeField(
        default=timezone.now
    )

    def __str__(self):
        return self.title


class DiscordAnnouncement(models.Model):

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['channel_id', 'message_id'],
                name="unique_announcement")
        ]
    author = models.CharField(
        max_length=1000,
        default=None
    )
    author_id = models.CharField(
        max_length=200,
        default=None
    )
    content = models.CharField(
        max_length=3000,
        default=None,
        null=True
    )
    date = NewPSTDateTimeField(
        default=timezone.now
    )
    channel_id = models.CharField(
        max_length=200,
        default=None,
        null=True
    )
    message_id = models.CharField(
        max_length=200,
        default=None,
        null=True
    )

    @property
    def get_html_content(self):
        formatted = self.content.replace("\n", " <br>")
        # if it is a special character
        special_characters = ')];\',.:"<'
        href_tag = r'[^\">]https?://\S* '
        matches = re.search(href_tag, formatted)
        while matches is not None:
            match = matches.regs[0]
            beginning = match[0]
            if formatted[beginning] != "h":
                beginning += 1
            end = beginning + formatted[match[0]+2:].find(" ")+1
            if formatted[end-1] in special_characters:
                end -= 1
            new_formatted = formatted.replace(
                formatted[beginning:end],
                f'<a target="_blank" href="{formatted[beginning:end]}">{formatted[beginning:end]}</a>'
            )
            matches = re.search(href_tag, new_formatted)
            formatted = new_formatted

        discord_emoji_tag = r'<:\w+:\d+>'
        matches = re.search(discord_emoji_tag, formatted)
        while matches is not None:
            match = matches.regs[0]
            emoji_tag_beginning = match[0]
            emoji_tag_end = emoji_tag_beginning + formatted[emoji_tag_beginning:].find(">")+1

            emoji_id_beginning = (
                emoji_tag_beginning +
                re.search(r"\d+", formatted[emoji_tag_beginning:end]).regs[0][0]
            )
            emoji_id_end = formatted[emoji_id_beginning:].find(">")
            emoji_id = formatted[emoji_id_beginning:emoji_id_beginning+emoji_id_end]

            new_formatted = formatted.replace(
                formatted[emoji_tag_beginning:emoji_tag_end],
                f'<img src="https://cdn.discordapp.com/emojis/{emoji_id}.webp?size=44">'
            )
            matches = re.search(discord_emoji_tag, new_formatted)
            formatted = new_formatted

        bold_markdown = r'\*\*[^*]*\*\*'
        matches = re.search(bold_markdown, formatted)
        while matches is not None:
            match = matches.regs[0]
            bold_tag_beginning = match[0]
            bold_tag_end = match[1]
            new_formatted = formatted.replace(
                formatted[bold_tag_beginning:bold_tag_end],
                f"<b>{formatted[bold_tag_beginning+2:bold_tag_end-2]}</b>"
            )
            matches = re.search(bold_markdown, new_formatted)
            formatted = new_formatted
        return formatted

    @property
    def sortable_date(self):
        return self.date.pst

    @staticmethod
    def get_date_for_message(discord_timestamp):
        from announcements.management.commands.process_announcements import SERVICE_NAME
        from csss.setup_logger import Loggers
        logger = Loggers.get_logger(logger_name=SERVICE_NAME)
        try:
            epoch_timestamp = datetime.datetime.strptime(discord_timestamp, "%Y-%m-%dT%H:%M:%S.%f%z").timestamp()
            logger.info(
                f"[get_date_for_message() ] got epoch_timestamp [{epoch_timestamp}] from discord_timestamp"
                f" {discord_timestamp}"
            )
        except Exception:
            epoch_timestamp = datetime.datetime.strptime(discord_timestamp, "%Y-%m-%dT%H:%M:%S%f%z").timestamp()
            logger.info(
                f"[get_date_for_message() ] got epoch_timestamp [{epoch_timestamp}] from discord_timestamp"
                f" {discord_timestamp}"
            )
        epoch_datetime_obj = pstdatetime.from_epoch(epoch_timestamp)
        logger.info(f"[get_date_for_message() ] "
                    f"got epoch_datetime_obj [{epoch_datetime_obj}] from epoch_timestamp {epoch_timestamp}]")
        logger.info(
            f"[get_date_for_message() ] epoch_datetime_obj [{epoch_datetime_obj}] convertable to"
            f" epoch_datetime_obj.pst {epoch_datetime_obj.pst}]"
        )
        return epoch_datetime_obj.pst


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
    discord_announcement = models.ForeignKey(
        DiscordAnnouncement,
        related_name='visibility_indicator',
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True
    )
    date = PSTDateTimeField(
        default=timezone.now
    )
    pst_date = NewPSTDateTimeField(
        default=None,
        null=True
    )
    author = models.CharField(
        max_length=200,
        default=None,
        blank=True
    )

    display = models.BooleanField(
        default=None,
        blank=True
    )

    @property
    def get_date(self):
        return self.date if self.pst_date is None else self.pst_date.pst

    @property
    def get_html_date(self):
        return self.date if self.pst_date is None else self.pst_date.pst.strftime("%Y-%m-%d %I:%M:%S %p %Z")

    def __str__(self):
        if self.email is None:
            return f"{self.manual_announcement}"
        else:
            return f"{self.email}"
