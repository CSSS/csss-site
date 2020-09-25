import datetime
import logging
from email.utils import parseaddr

import pandas
import pytz
from django.conf import settings
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
    help = "process the latest new emails and manual announcements and determines which to display"

    def handle(self, *args, **options):
        logger.info(options)
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
        messages.sort(key=lambda x: x.sortable_date, reverse=True)
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
                Announcement(term=term, post=message, date=announcement_datetime,
                             display=True, author=message.author).save()
                logger.info("[process_announcements handle()] saved post from"
                            f" {message.author} with date {announcement_datetime} "
                            f"for term {term}")


def add_sortable_date_to_email(email):
    """
    attempts to get add a sortable date to the email using a field in the email.
    Failing that, it will just return today's date.

    Keyword Argument
    email_date -- the email

    Return
    email_datetime -- the email with a new "sortable_date" field
    """
    # will modify the processed date to be change
    # from the day the mailbox was polled to the date the email was sent
    email_date = email.get_email_object().get('date')
    successful = False
    email_datetime = None
    date_format = '%a, %d %b %Y %H:%M:%S %z'
    if email.subject == "The CSSS is seeking Mentors for SFU CSSS Frosh Week 2020":
        print(1)
    try:
        email_datetime = datetime.datetime.strptime(email_date, date_format).astimezone(
            pytz.timezone(settings.WEBSITE_TIME_ZONE)
        )
        successful = True
    except ValueError:
        logger.info(f"[process_announcements get_date_from_email()] date '{email_date}' "
                    f"does not match format '{date_format}'")
    if not successful:
        date_format = '%a, %d %b %Y %H:%M:%S %z'
        try:
            email_datetime = datetime.datetime.strptime(email_date[:-6], date_format).astimezone(
                pytz.timezone(settings.WEBSITE_TIME_ZONE)
            )
            successful = True
        except ValueError:
            logger.info(f"[process_announcements get_date_from_email()] date '{email_date[:-6]}' "
                        f"does not match format '{date_format}'")
    if not successful:
        date_format = '%a, %d %b %Y %H:%M:%S %Z'
        try:
            email_datetime = datetime.datetime.strptime(email_date, date_format).astimezone(
                pytz.timezone(settings.WEBSITE_TIME_ZONE)
            )
            successful = True
        except ValueError:
            logger.info(f"[process_announcements get_date_from_email()] date '{email_date}' "
                        f"does not match format '{date_format}'")
            email_datetime = datetime.date.today()
    if not successful:
        logger.info("[process_announcements get_date_from_email()] ultimately unable to "
                    f"determine the format for date {email_date}. Reverting to current date")
    else:
        logger.info(f"[process_announcements get_date_from_email()] date '{email_date}' "
                    f"from email transformed to datetime object {email_datetime}")
    email.sortable_date = email_datetime
    return email


def add_sortable_date_to_manual_announcement(timezone_difference, manual_announcement):
    """
    create the sortable_date for the manual announcement

    Keyword Argument
    manual_announcement -- the manual announcement whose date needs to be made sortable

    Return
    manual_announcement -- a manual announcement with an additional sortable_date property
    """
    manual_announcement.sortable_date = \
        pytz.timezone(settings.WEBSITE_TIME_ZONE).localize(
            manual_announcement.date + datetime.timedelta(hours=timezone_difference)
        )
    logger.info('[process_announcements return_manual_announcement_with_date)] generated '
                f'date {manual_announcement.sortable_date} from date {manual_announcement.date}')
    return manual_announcement


def get_timezone_difference(date, tz1, tz2):
    """
    Returns the difference in hours between timezone1 and timezone2
    for a given date.
    """
    tz1_timezone = pytz.timezone(tz1)
    tz2_timezone = pytz.timezone(tz2)
    date = pandas.to_datetime(date)
    return (tz1_timezone.localize(date) - tz2_timezone.localize(date).astimezone(tz1_timezone)).seconds / 3600


def get_officer_term_mapping():
    """
    creates a dictionary containing all relevant emails for all terms

    return
    officer_mapping - a dictionary where the key is the term number (e.g. 20202)
    and the values is a list of valid emails
    """
    officer_mapping = {}
    for term in Term.objects.all().order_by('term_number'):
        term_number = f"{term.term_number}"
        for officer in Officer.objects.all().filter(elected_term=term):
            if term_number not in officer_mapping:
                officer_mapping[term_number] = []
            if len(officer.sfuid) > 0 and f"{officer.sfuid}@sfu.ca" not in officer_mapping[term_number]:
                officer_mapping[term_number].append(f"{officer.sfuid}@sfu.ca")
            if len(officer.sfu_email_alias) > 0 and f"{officer.sfu_email_alias}@sfu.ca" not in officer_mapping[
                term_number]:
                officer_mapping[term_number].append(f"{officer.sfu_email_alias}@sfu.ca")
            for announcement_emails in AnnouncementEmailAddress.objects.all().filter(officer=officer):
                if announcement_emails.email not in officer_mapping[term_number]:
                    officer_mapping[term_number].append(announcement_emails.email)
    return officer_mapping
