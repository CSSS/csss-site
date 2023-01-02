import logging
from time import sleep

from about.models import UnProcessedOfficer, Officer
from csss.views.send_discord_dm import send_discord_dm

logger = logging.getLogger('csss_site')


def run_job():
    unprocessed_officers = UnProcessedOfficer.objects.all()
    current_director_of_archives = Officer.objects.all().filter(
        position_name='Director of Archives'
    ).order_by('-start_date').first()
    current_systems_admin = Officer.objects.all().filter(
        position_name='Systems Administrator'
    ).order_by('-start_date').first()
    for unprocessed_officer in unprocessed_officers:
        sleep(1)
        unprocessed_officer.number_of_nags += 1
        unprocessed_officer.save()
        if (unprocessed_officer.number_of_nags % 3) == 0:
            send_discord_dm(
                current_systems_admin.discord_id, "unfilled in officer data",
                f"{unprocessed_officer.full_name} still has not filled in their data..."
            )
        if current_director_of_archives is not None:
            send_discord_dm(
                current_director_of_archives.discord_id, "unfilled in officer data",
                f"{unprocessed_officer.full_name} still has not filled in their data..."
            )
        logger.info(
            f"[about/nag_officers_to_enter_info.py()] alerted the Sys Admin and DoA that "
            f"{unprocessed_officer.full_name} has not filled in their info"
        )
