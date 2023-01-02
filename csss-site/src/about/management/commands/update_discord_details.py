import datetime
from time import perf_counter, sleep

from django.core.management import BaseCommand

from about.models import Officer
from about.views.commands.update_discord_details import run_job
from about.views.input_new_officers.enter_new_officer_info.utils.get_discord_username_and_nickname import \
    get_discord_username_and_nickname
from csss.models import CronJob, CronJobRunStat
from csss.setup_logger import date_timezone, Loggers

SERVICE_NAME = "update_discord_details"

class Command(BaseCommand):
    help = "get the latest discord name and nicknames for the officers"

    def handle(self, *args, **options):
        run_job()
        time1 = perf_counter()
        current_date = datetime.datetime.now(date_timezone)
        logger = Loggers.get_logger(logger_name=SERVICE_NAME)
        all_officers = Officer.objects.all()
        officers = all_officers.exclude(discord_id="NA")
        officers_discord_ids = list(set(list(officers.values_list('discord_id', flat=True))))
        discord_info_maps = {}
        max_retries = 5
        for officers_discord_id in officers_discord_ids:
            sleep(1)
            success, error_message, discord_username, discord_nickname = get_discord_username_and_nickname(
                officers_discord_id
            )
            retries = 0
            while not success and retries < max_retries:
                sleep(10)
                success, error_message, discord_username, discord_nickname = get_discord_username_and_nickname(
                    officers_discord_id
                )
                retries += 1
            officer = officers.filter(discord_id=officers_discord_id).first()
            if success:
                if discord_username != officer.discord_username or discord_nickname != officer.discord_nickname:
                    logger.info(
                        f"[about/update_discord_details.py()] the nickname or username for {officer.full_name} "
                        f"was update since last time"
                    )
                    discord_info_maps[officer.sfu_computing_id] = {
                        'officers_discord_id': officers_discord_id,
                        'discord_username': discord_username,
                        'discord_nickname': discord_nickname
                    }
                else:
                    logger.info(
                        f"[about/update_discord_details.py()] the nickname or username for {officer.full_name} "
                        f"was not updated since last time"
                    )
            else:
                logger.info(
                    f"[about/update_discord_details.py()] unable to get the discord username and nickname for "
                    f"{officer.full_name} due to error {error_message}"
                )
        officers_to_change = all_officers.filter(sfu_computing_id__in=list(discord_info_maps.keys()))

        for officer in officers_to_change:
            officer.discord_id = discord_info_maps[officer.sfu_computing_id]['officers_discord_id']
            officer.discord_username = discord_info_maps[officer.sfu_computing_id]['discord_username']
            nickname = discord_info_maps[officer.sfu_computing_id]['discord_nickname']
            officer.discord_nickname = nickname if nickname is not None else "NA"
        Officer.objects.bulk_update(officers_to_change, ['discord_id', 'discord_username', 'discord_nickname'])
        time2 = perf_counter()
        total_seconds = time2 - time1
        cron_job = CronJob.objects.get(job_name=SERVICE_NAME)
        number_of_stats = CronJobRunStat.objects.all().filter(job=cron_job)
        if len(number_of_stats) == 10:
            first = number_of_stats.order_by('id').first()
            if first is not None:
                first.delete()
        CronJobRunStat(job=cron_job, run_time_in_seconds=total_seconds).save()
        Loggers.remove_logger(SERVICE_NAME, current_date)
