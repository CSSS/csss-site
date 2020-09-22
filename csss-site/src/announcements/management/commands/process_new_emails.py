import datetime
import logging
from email.utils import parseaddr

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand
from django_mailbox.models import Message

from about.models import AnnouncementEmailAddress, Term
from announcements.models import PostsAndEmails
from csss.views_helper import get_current_term

logger = logging.getLogger('csss_site')

NUMBER_OF_POSTS_PER_PAGE = 5


class Command(BaseCommand):
    help = "process new emails using the django_mailbox app and determines whether or not to show them"

    def handle(self, *args, **options):
        logger.info(options)
        un_processed_emails = Message.objects.all().filter(email__isnull=True).order_by('-id')
        email_list_for_current_term = get_sfu_email_for_current_term()
        if email_list_for_current_term is None:
            logger.info("Unable to get the email list for the current term")
        else:
            for un_processed_email in un_processed_emails:
                logger.info(f"processing email {un_processed_email}")
                announcement = PostsAndEmails(email=un_processed_email)
                announcement.show = un_processed_email.from_address[0] in email_list_for_current_term
                logger.info(f"email from {un_processed_email.from_address[0]}'s shown attribute is set to {announcement.show}")
                announcement.page_number = 0
                logger.info(f"page number for email from {un_processed_email} set to {announcement.page_number}")
                announcement.save()
                if announcement.show:
                    # will modify the processed date to be change
                    # from the day the mailbox was polled to the date the email was sent
                    try:
                        email_date = datetime.datetime.strptime(un_processed_email.get_email_object().get('date'),
                                                                '%a, %d %b %Y %H:%M:%S %z')
                    except ValueError:
                        email_date = datetime.datetime.strptime(un_processed_email.get_email_object().get('date')[:-6],
                                                                '%a, %d %b %Y '
                                                                '%H:%M:%S %z')
                    un_processed_email.processed = email_date
                    un_processed_email.from_header = parseaddr(un_processed_email.from_header)[0]
                    logger.info(f"date and from_header for email {un_processed_email} set to {email_date} and {un_processed_email.from_header}")
                    un_processed_email.save()


def get_sfu_email_for_current_term():
    try:
        current_term = Term.objects.get(term_number=get_current_term())
    except ObjectDoesNotExist:
        return None
    sfu_emails = [email.email for email in AnnouncementEmailAddress.objects.all().filter(officer__elected_term=current_term)]
    return sfu_emails