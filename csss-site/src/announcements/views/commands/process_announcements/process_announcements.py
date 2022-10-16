import datetime
from email.utils import parseaddr

from django.conf import settings
from django_mailbox.models import Mailbox
from django_mailbox.models import Message

from about.models import Term, UnProcessedOfficer
from announcements.models import Announcement, ManualAnnouncement
from announcements.views.commands.process_announcements.add_sortable_date_to_email import add_sortable_date_to_email
from announcements.views.commands.process_announcements.add_sortable_date_to_manual_announcement import \
    add_sortable_date_to_manual_announcement
from announcements.views.commands.process_announcements.get_officer_term_mapping import get_officer_term_mapping
from announcements.views.commands.process_announcements.get_timezone_difference import get_timezone_difference
from csss.setup_logger import get_logger
from csss.views_helper import get_term_number_for_specified_year_and_month

logger = get_logger()


def django_mailbox_handle():
    # duplicate of django_mailbox/management/commands/getmail.py
    mailboxes = Mailbox.active_mailboxes.all()
    for mailbox in mailboxes:
        logger.info(
            'Gathering messages for %s',
            mailbox.name
        )
        messages = mailbox.get_new_mail()
        for message in messages:
            logger.info(
                'Received %s (from %s)',
                message.subject,
                message.from_address
            )


def run_job(poll_email=True):
    if len(UnProcessedOfficer.objects.all()) > 0:
        return
    if poll_email:
        django_mailbox_handle()

    time_difference = get_timezone_difference(
        datetime.datetime.now().strftime('%Y-%m-%d'),
        settings.WEBSITE_TIME_ZONE,
        settings.TIME_ZONE_FOR_PREVIOUS_WEBSITE
    )

    messages = []
    messages.extend(
        [add_sortable_date_to_email(email) for email in
         Message.objects.all().filter(visibility_indicator__isnull=True)]
    )
    messages.extend(
        [add_sortable_date_to_manual_announcement(time_difference, manual_announcement)
         for manual_announcement in ManualAnnouncement.objects.all().filter(visibility_indicator__isnull=True)]
    )
    messages.sort(key=lambda x: x.sortable_date, reverse=False)
    officer_mapping = get_officer_term_mapping()

    for message in messages:
        announcement_datetime = message.sortable_date
        term_number = get_term_number_for_specified_year_and_month(
            announcement_datetime.month,
            announcement_datetime.year
        )
        if f"{term_number}" not in officer_mapping:
            logger.info("[process_announcements handle()] announcement with date "
                        f"{announcement_datetime} does not map to a term")
            continue
        term = Term.objects.all().filter(term_number=term_number)
        if len(term) == 0:
            logger.info("[process_announcements handle()] could not find a valid term "
                        f"for term_number {term_number}")
            continue
        term = term[0]
        if hasattr(message, 'mailbox'):
            officer_emails = officer_mapping[f"{term_number}"]
            logger.info(f"[process_announcements handle()] acquired {len(officer_emails)} "
                        f"officers for date {announcement_datetime}")

            if len(parseaddr(message.from_header)) > 0:
                author_name = parseaddr(message.from_header)[0]
                author_email = parseaddr(message.from_header)[1]
                valid_email = (author_email in officer_emails)
                if valid_email:
                    print(1)
                Announcement(term=term, email=message, date=announcement_datetime,
                             display=valid_email, author=author_name).save()
                logger.info("[process_announcements handle()] saved email from"
                            f" {author_name} with email {author_email} with date {announcement_datetime} "
                            f"for term {term}. Will {'not ' if valid_email is False else ''}display email")
            else:
                Announcement(term=term, email=message, date=announcement_datetime,
                             display=False).save()
                logger.info("[process_announcements handle()] unable to determine sender of email "
                            f"with date {announcement_datetime} "
                            f"for term {term}. Will not display email")
        else:
            Announcement(term=term, manual_announcement=message, date=announcement_datetime,
                         display=True, author=message.author).save()
            logger.info("[process_announcements handle()] saved post from"
                        f" {message.author} with date {announcement_datetime} "
                        f"for term {term}")
