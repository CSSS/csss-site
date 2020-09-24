import datetime
import logging
from email.utils import parseaddr

import pytz
from django.core.management.base import BaseCommand
from django_mailbox.models import Message
from django_mailbox.models import Mailbox

from about.models import Officer, Term, AnnouncementEmailAddress
from announcements.models import Announcement, ManualAnnouncement
from csss.views_helper import get_term_number_for_specified_year_and_month

logger = logging.getLogger('csss_site')


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


class Command(BaseCommand):
    help = "process the latest new emails and determines which to display"

    def handle(self, *args, **options):
        logger.info(options)
        django_mailbox_handle()

        messages = []
        for message in Message.objects.all().filter(visibility_indicator__isnull=True):
            message.processed = get_date_from_email(message.get_email_object().get('date')).replace(tzinfo=pytz.utc)
            messages.append(message)
        for post in ManualAnnouncement.objects.all().filter(visibility_indicator__isnull=True):
            post.processed = post.processed.replace(tzinfo=pytz.utc)
            messages.append(post)
        messages.sort(key=lambda x: x.processed, reverse=True)
        officer_mapping = get_officer_term_mapping()

        for message in messages:
            announcement_datetime = message.processed
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
                    Announcement(term=term, email=message, date=announcement_datetime,
                                 display=valid_email, author=author_name).save()
                    logger.info("[process_announcements handle()] saved email from"
                                f" {author_name} with email {author_email} with date {announcement_datetime} "
                                f"for term {term}. Will {'not' if valid_email is False else ''} email")
                else:
                    Announcement(term=term, email=message, date=announcement_datetime,
                                 display=False).save()
                    logger.info("[process_announcements handle()] unable to determine sender of email "
                                f"with date {announcement_datetime} "
                                f"for term {term}. Will not display email")
            else:
                Announcement(term=term, post=message, date=announcement_datetime,
                             display=True, author=message.author).save()
                logger.info("[process_announcements handle()] saved post from"
                            f" {message.author} with date {announcement_datetime} "
                            f"for term {term}")


def get_date_from_email(email_date):
    # will modify the processed date to be change
    # from the day the mailbox was polled to the date the email was sent
    successful = False
    announcement_datetime = None
    date_format = '%a, %d %b %Y %H:%M:%S %z'
    try:
        announcement_datetime = datetime.datetime.strptime(email_date, date_format)
        successful = True
    except ValueError:
        logger.info(f"[process_announcements get_date_from_email()] date '{email_date}' "
                    f"does not match format '{date_format}'")
    if not successful:
        date_format = '%a, %d %b %Y %H:%M:%S %z'
        try:
            announcement_datetime = datetime.datetime.strptime(email_date[:-6], date_format)
            successful = True
        except ValueError:
            logger.info(f"[process_announcements get_date_from_email()] date '{email_date[:-6]}' "
                        f"does not match format '{date_format}'")
    if not successful:
        date_format = '%a, %d %b %Y %H:%M:%S %Z'
        try:
            announcement_datetime = datetime.datetime.strptime(email_date, date_format)
            successful = True
        except ValueError:
            logger.info(f"[process_announcements get_date_from_email()] date '{email_date}' "
                        f"does not match format '{date_format}'")
            announcement_datetime = datetime.date.today()
    if not successful:
        logger.info("[process_announcements get_date_from_email()] ultimately unable to "
                    f"determine the format for date {email_date}. Reverting to current date")
    else:
        logger.info(f"[process_announcements get_date_from_email()] date '{email_date}' "
                    f"from email transformed to datetime object {announcement_datetime}")
    return announcement_datetime


def get_officer_term_mapping():
    officer_mapping = {}
    for term in Term.objects.all().order_by('term_number'):
        term_number = f"{term.term_number}"
        for officer in Officer.objects.all().filter(elected_term=term):
            if term_number not in officer_mapping:
                officer_mapping[term_number] = []
            if f"{officer.sfuid}@sfu.ca" not in officer_mapping[term_number]:
                officer_mapping[term_number].append(f"{officer.sfuid}@sfu.ca")
            if f"{officer.sfu_email_alias}@sfu.ca" not in officer_mapping[term_number]:
                officer_mapping[term_number].append(f"{officer.sfu_email_alias}@sfu.ca")
            for announcement_emails in AnnouncementEmailAddress.objects.all().filter(officer=officer):
                if announcement_emails.email not in officer_mapping[term_number]:
                    officer_mapping[term_number].append(announcement_emails.email)
    return officer_mapping
