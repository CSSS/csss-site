import calendar
import time

from django.core.management import BaseCommand

from about.models import Officer, UnProcessedOfficer
from csss.models import CronJob, CronJobRunStat
from csss.setup_logger import Loggers
from csss.views.pstdatetime import pstdatetime
from csss.views.send_discord_dm import send_discord_dm
from csss.views.send_discord_group_message import send_discord_group_message
from csss.views_helper import get_next_term_obj

SERVICE_NAME = "nag_doa_to_generate_links"


class Command(BaseCommand):

    def handle(self, *args, **options):
        time1 = time.perf_counter()
        logger = Loggers.get_logger(logger_name=SERVICE_NAME)
        current_director_of_archives = Officer.objects.all().filter(
            position_name='Director of Archives'
        ).order_by('-start_date').first()

        """        
        After Discussing with https://github.com/dinazeng, she proposed the following nag logic
        1 month before term ends
        2 weeks before finals
        during finals
        another 1 after finals

        However, since the date when finals are seems to be very in flux as can be seen from the below links:
        1. https://web.archive.org/web/20230324103748/http://www.sfu.ca/students/calendar/2023/spring/academic-dates/2023.html # noqa E501
        2. https://web.archive.org/web/20240115012622/https://www.sfu.ca/students/calendar/2024/spring/academic-dates/2024.html # noqa E501
        I chose to implement a logic that is more dependent on the week number in the last month than on which weeks
         in the last months have finals

        So once a month is left in a term:
        1. the DoA will be nagged once a week on Monday till the last 2 week
        2. then the DoA wil be nagged every 2 days in the second to last week
        3. then the Doa will be nagged every day in the last week
        """
        today_date = pstdatetime.now()

        next_term = get_next_term_obj()
        officer_already_created_for_next_term = next_term and next_term.officer_set.all().count() > 0
        officer_generation_links_not_created = UnProcessedOfficer.objects.all().count() == 0
        one_month_before_term_ends = today_date.month % 4 == 0

        logger.info(f"[about/nag_doa_to_generate_links.py()] next_term={next_term}")
        logger.info(
            f"[about/nag_doa_to_generate_links.py()] officer_already_created_for_next_term="
            f"{officer_already_created_for_next_term}"
        )
        logger.info(
            f"[about/nag_doa_to_generate_links.py()] officer_generation_links_not_created"
            f"={officer_generation_links_not_created}"
        )
        logger.info(
            f"[about/nag_doa_to_generate_links.py()] current_director_of_archives={current_director_of_archives}"
        )
        logger.info(f"[about/nag_doa_to_generate_links.py()] one_month_before_term_ends={one_month_before_term_ends}")
        doa_has_to_be_nagged = (
            not officer_already_created_for_next_term and officer_generation_links_not_created and
            current_director_of_archives and one_month_before_term_ends
        )
        logger.info(f"[about/nag_doa_to_generate_links.py()] doa_has_to_be_nagged={doa_has_to_be_nagged}")
        if doa_has_to_be_nagged:
            title = "Officer Links Need to be Generated for Next Term"
            text_content = f"<@{current_director_of_archives.discord_id}>"
            message = (
                f"Hi <@{current_director_of_archives.discord_id}>,\n\nlooks like you haven't generated "
                f"the needed officer links so that execs have access to what they need next term. Please refer "
                f"to [this page](https://sfucsss.org/about/specify_new_officers) for link generation."
            )

            number_of_weeks_in_month = len(calendar.month(today_date.year, today_date.month).split('\n')) - 3
            logger.info(f"[about/nag_doa_to_generate_links.py()] number_of_weeks_in_month={number_of_weeks_in_month}")
            week_number = today_date.isocalendar()[1]
            logger.info(f"[about/nag_doa_to_generate_links.py()] week_number={week_number}")
            second_to_last_week = week_number + 2 == number_of_weeks_in_month
            logger.info(f"[about/nag_doa_to_generate_links.py()] second_to_last_week={second_to_last_week}")
            last_week = week_number + 1 == number_of_weeks_in_month
            logger.info(f"[about/nag_doa_to_generate_links.py()] last_week={last_week}")
            if last_week:
                if today_date.day % 3 == 0:
                    logger.info("[about/nag_doa_to_generate_links.py()] sending nag to exec chat in the last week")
                    send_discord_group_message(
                        573280123285929994, title, message, text_content=text_content
                    )
                logger.info("[about/nag_doa_to_generate_links.py()] sending nag to DoA directly in the last week")
                send_discord_dm(current_director_of_archives.discord_id, title, message)
            elif second_to_last_week:
                if today_date.day % 2 == 0:
                    if today_date.day % 4 == 0:
                        logger.info(
                            "[about/nag_doa_to_generate_links.py()] sending nag to exec chat in second to last week"
                        )
                        send_discord_group_message(
                            573280123285929994, title, message, text_content=text_content
                        )
                    logger.info(
                        "[about/nag_doa_to_generate_links.py()] sending nag to DoA directly in the second to last "
                        "week"
                    )
                    send_discord_dm(current_director_of_archives.discord_id, title, message)
            else:
                if today_date.weekday() == 0:
                    logger.info(
                        "[about/nag_doa_to_generate_links.py()] sending nag to DoA directly on a Monday in the last "
                        "month"
                    )
                    send_discord_dm(current_director_of_archives.discord_id, title, message)
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
