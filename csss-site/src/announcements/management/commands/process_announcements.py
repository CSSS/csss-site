import datetime
import time
from email.utils import parseaddr

from django.conf import settings
from django.core.management.base import BaseCommand
from django_mailbox.management.commands.getmail import Command as GetMailCommand
from django_mailbox.models import Message

from about.models import UnProcessedOfficer, Term
from announcements.models import ManualAnnouncement, Announcement
from announcements.views.commands.process_announcements.add_sortable_date_to_email import add_sortable_date_to_email
from announcements.views.commands.process_announcements.add_sortable_date_to_manual_announcement import \
    add_sortable_date_to_manual_announcement
from announcements.views.commands.process_announcements.get_officer_term_mapping import get_officer_term_mapping
from announcements.views.commands.process_announcements.get_timezone_difference import get_timezone_difference
from csss.models import CronJob, CronJobRunStat
from csss.setup_logger import Loggers, date_timezone
from csss.views_helper import get_term_number_for_specified_year_and_month

SERVICE_NAME = "process_announcements"


class Command(BaseCommand):
    help = "process the latest new emails and manual announcements and determines which to display"

    def add_arguments(self, parser):
        parser.add_argument(
            '--poll_email',
            action='store_true',
            default=False,
            help="pull the latest emails from gmail"
        )

    def handle(self, *args, **options):
        logger = Loggers.get_logger(logger_name=SERVICE_NAME)
        logger.info(options)
        time1 = time.perf_counter()
        current_date = datetime.datetime.now(date_timezone)
        if len(UnProcessedOfficer.objects.all()) > 0:
            return
        if options['poll_email']:
            GetMailCommand().handle()

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
        time2 = time.perf_counter()
        total_seconds = time2 - time1
        cron_job = CronJob.objects.get(job_name=SERVICE_NAME)
        number_of_stats = CronJobRunStat.objects.all().filter(job=cron_job)
        if len(number_of_stats) == 10:
            first = number_of_stats.order_by('id').first()
            if first is not None:
                first.delete()
        CronJobRunStat(job=cron_job, run_time_in_seconds=total_seconds).save()
        Loggers.remove_logger(SERVICE_NAME, current_date)
