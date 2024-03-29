import time

from django.core.management import BaseCommand
from django.db.models import Q

from about.models import OfficerEmailListAndPositionMapping
from csss.models import CronJob, CronJobRunStat
from csss.setup_logger import Loggers
from csss.views.pstdatetime import pstdatetime
from csss.views.send_discord_dm import send_discord_dm
from csss.views.send_discord_group_message import send_discord_group_message
from csss.views_helper import get_current_term_obj
from elections.models import Election

SERVICE_NAME = "remind_election_officer_to_provide_websurvey_link"


class Command(BaseCommand):

    def handle(self, *args, **options):
        time1 = time.perf_counter()
        logger = Loggers.get_logger(logger_name=SERVICE_NAME)
        today_date = pstdatetime.now()
        elections_missing_websurvey_link = Election.objects.all().filter(
            (Q(websurvey__isnull=True) | Q(websurvey='NA')) & Q(date__lte=today_date)
        ).exclude(slug="2015-04-04-general_election").order_by('-date')
        logger.info(
            f"[elections/remind_election_officer_to_provide_websurvey_link.py()] got "
            f"{len(elections_missing_websurvey_link)} elections that are missing websurvey links"
        )
        elections_missing_websurvey_link = [
            (
                f"[{election_missing_websurvey_link.human_friendly_name}]"
                f"(https://sfucsss.org/elections/{election_missing_websurvey_link.slug}"
                f"/election_modification_nominee_links/)"
            )
            for election_missing_websurvey_link in elections_missing_websurvey_link
        ]
        current_term = get_current_term_obj()
        logger.info(
            f"[elections/remind_election_officer_to_provide_websurvey_link.py()] current_term = {current_term}"
        )
        if len(elections_missing_websurvey_link) > 0 and current_term:
            elections_missing_websurvey_link = ", ".join(elections_missing_websurvey_link)
            logger.info(
                f"[elections/remind_election_officer_to_provide_websurvey_link.py()] "
                f"elections_missing_websurvey_link = {elections_missing_websurvey_link}"
            )
            election_officer_positions = list(OfficerEmailListAndPositionMapping.objects.all().filter(
                election_officer=True
            ).values_list('position_name', flat=True))
            logger.info(
                f"[elections/remind_election_officer_to_provide_websurvey_link.py()] election_officer_positions = "
                f"{election_officer_positions}"
            )
            discord_tag_for_latest_election_officer_in_current_term = current_term.officer_set.filter(
                position_name__in=election_officer_positions
            ).values_list('discord_id', flat=True).order_by('-start_date')[0]
            logger.info(
                f"[elections/remind_election_officer_to_provide_websurvey_link.py()] "
                f"discord_tag_for_latest_election_officer_in_current_term = "
                f"{discord_tag_for_latest_election_officer_in_current_term}"
            )
            issue_with_dming_users = False
            logger.info(
                f"[elections/remind_election_officer_to_provide_websurvey_link.py()] "
                f"sending message to {discord_tag_for_latest_election_officer_in_current_term} "
                f"regarding adding the websurvey link"
            )
            success, error_message = send_discord_dm(
                discord_tag_for_latest_election_officer_in_current_term, "Missing Election Websurvey Link",
                (
                    f"Looks like you may have forgotten to "
                    f"add the websurvey link to: {elections_missing_websurvey_link}"
                )
            )
            if not success:
                logger.warning(
                    f"[elections/remind_election_officer_to_provide_websurvey_link.py()] {error_message}"
                )
                issue_with_dming_users = True
            logger.info(
                f"[elections/remind_election_officer_to_provide_websurvey_link.py()] issue_with_dming_users = "
                f"{issue_with_dming_users}"
            )
            if issue_with_dming_users or today_date.day % 2 == 0:
                discord_tag_for_latest_election_officer_in_current_term = (
                    f"<@{discord_tag_for_latest_election_officer_in_current_term}>"
                )
                logger.info(
                    f"[elections/remind_election_officer_to_provide_websurvey_link.py()] "
                    f"discord_tag_for_latest_election_officer_in_current_term = "
                    f"{discord_tag_for_latest_election_officer_in_current_term}"
                )
                logger.info(
                    "[elections/remind_election_officer_to_provide_websurvey_link.py()] sending message to"
                    " exec chat regarding saving election websurvey link"
                )
                success, error_message = send_discord_group_message(
                    573280123285929994, "Missing Election Websurvey Link",
                    (
                        f"Looks like {discord_tag_for_latest_election_officer_in_current_term}"
                        f" has not yet added the websurvey link to the election {elections_missing_websurvey_link}"
                     ),
                    text_content=discord_tag_for_latest_election_officer_in_current_term
                )
                if not success:
                    logger.error(
                        f"[elections/remind_election_officer_to_provide_websurvey_link.py()] {error_message}"
                    )
        time2 = time.perf_counter()
        total_seconds = time2 - time1
        cron_job = CronJob.objects.get(job_name=SERVICE_NAME)
        number_of_stats = CronJobRunStat.objects.all().filter(job=cron_job)
        if len(number_of_stats) == 10:
            first = number_of_stats.order_by('id').first()
            if first is not None:
                first.delete()
        CronJobRunStat(job=cron_job, run_time_in_seconds=total_seconds).save()
        Loggers.remove_logger(SERVICE_NAME)
