import time

from django.core.management import BaseCommand

from about.models import OfficerEmailListAndPositionMapping
from csss.models import CronJob, CronJobRunStat
from csss.setup_logger import Loggers
from csss.views.pstdatetime import pstdatetime
from csss.views.send_discord_dm import send_discord_dm
from csss.views.send_discord_group_message import send_discord_group_message
from csss.views_helper import get_current_term_obj
from elections.models import Election, VoterChoice

SERVICE_NAME = "nag_election_officer_share_results"


class Command(BaseCommand):

    def handle(self, *args, **options):
        time1 = time.perf_counter()
        logger = Loggers.get_logger(logger_name=SERVICE_NAME)
        today_date = pstdatetime.now()
        election_with_end_dates = Election.objects.all().filter(end_date__isnull=False).order_by('-date')
        logger.info(
            f"[elections/nag_election_officer_share_results.py() ] got {len(election_with_end_dates)} elections "
            f"that have end dates"
        )
        elections_with_missing_results = []
        for election_with_end_date in election_with_end_dates:
            no_results_detected = VoterChoice.objects.all().filter(
                selection__nominee_speech__nominee__election_id=election_with_end_date.id
            ).count() == 0
            if election_with_end_date.end_date < today_date and no_results_detected:
                logger.info(
                    f"[elections/nag_election_officer_share_results.py() ] determined "
                    f"{election_with_end_date.human_friendly_name} should have votes but doesn't seem to have them"
                )
                elections_with_missing_results.append(election_with_end_date.human_friendly_name)
        elections_with_missing_results = ", ".join(elections_with_missing_results)
        logger.info(
            f"[elections/nag_election_officer_share_results.py() ] elections_with_missing_results = "
            f"{elections_with_missing_results}"
        )
        current_term = get_current_term_obj()
        logger.info(
            f"[elections/nag_election_officer_share_results.py() ] current_term = {current_term}"
        )
        if current_term:
            election_officer_positions = list(OfficerEmailListAndPositionMapping.objects.all().filter(
                election_officer=True
            ).values_list('position_name', flat=True))
            logger.info(
                f"[elections/nag_election_officer_share_results.py() ] election_officer_positions = "
                f"{election_officer_positions}"
            )
            discord_tag_for_election_officers_in_current_term = list(
                current_term.officer_set.filter(position_name__in=election_officer_positions)
                .values_list('discord_id', flat=True)
            )
            logger.info(
                f"[elections/nag_election_officer_share_results.py() ] "
                f"discord_tag_for_election_officers_in_current_term = "
                f"{discord_tag_for_election_officers_in_current_term}"
            )
            issue_with_dming_users = False
            for discord_tag_for_election_officer_in_current_term in discord_tag_for_election_officers_in_current_term:
                logger.info(
                    f"[elections/nag_election_officer_share_results.py() ] "
                    f"sending message to {discord_tag_for_election_officer_in_current_term} "
                    f"regarding saving election results"
                )
                success, error_message = send_discord_dm(
                    discord_tag_for_election_officer_in_current_term, "Missing Election Results",
                    (
                        f"Looks like you may have forgotten to "
                        f"upload the election results for: {elections_with_missing_results}\n\n"
                        f"If you are not sure how to upload the results, please refer to "
                        f"[the documentation](https://sfucsss.org/elections/election_officer_docum"
                        f"entation#5-results-collected)"
                    )
                )
                if not success:
                    logger.warning(f"[elections/nag_election_officer_share_results.py() ] {error_message}")
                    issue_with_dming_users = True
            logger.info(
                f"[elections/nag_election_officer_share_results.py() ] issue_with_dming_users = "
                f"{issue_with_dming_users}"
            )
            if issue_with_dming_users or today_date.day % 3 == 0:
                discord_tag_for_election_officers_in_current_term = [
                    f"<@{discord_tag_for_election_officer_in_current_term}>"
                    for discord_tag_for_election_officer_in_current_term in
                    discord_tag_for_election_officers_in_current_term
                ]
                logger.info(
                    f"[elections/nag_election_officer_share_results.py() ] "
                    f"discord_tag_for_election_officers_in_current_term = "
                    f"{discord_tag_for_election_officers_in_current_term}"
                )
                election_officer_tag = ", ".join(discord_tag_for_election_officers_in_current_term[:-1])
                if len(discord_tag_for_election_officers_in_current_term) > 1:
                    election_officer_tag += f" or {discord_tag_for_election_officers_in_current_term[-1]}"
                logger.info(
                    f"[elections/nag_election_officer_share_results.py() ] election_officer_tag ="
                    f" {election_officer_tag}"
                )
                logger.info(
                    "[elections/nag_election_officer_share_results.py() ] sending message to exec chat regarding "
                    "saving election results"
                )
                success, error_message = send_discord_group_message(
                    573280123285929994, "Missing Election Results",
                    (
                        f"Looks like {election_officer_tag} election officer[s] have not yet upload the election "
                        f"results for election[s] using [these instructions](https://sfucsss.org/elections/"
                        f"election_officer_documentation#5-results-collected): {elections_with_missing_results}"
                     )
                )
                if not success:
                    logger.error(f"[elections/nag_election_officer_share_results.py() ] {error_message}")
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
