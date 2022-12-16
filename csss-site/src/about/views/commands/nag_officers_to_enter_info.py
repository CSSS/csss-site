from about.models import UnProcessedOfficer, Officer
from about.views.input_new_officers.specify_new_officers.notifications. \
    send_notification_asking_officer_to_fill_in_form import \
    send_notification_asking_officer_to_fill_in_form
from csss.setup_logger import get_or_setup_logger
from csss.views.send_discord_dm import send_discord_dm


def run_job():
    logger = get_or_setup_logger("nag_officers_to_enter_info")
    unprocessed_officers = UnProcessedOfficer.objects.all()
    officers = Officer.objects.all()
    for unprocessed_officer in unprocessed_officers:
        success, error_message = send_notification_asking_officer_to_fill_in_form(
            unprocessed_officer.discord_id,
            unprocessed_officer.full_name,
            officers.filter(sfu_computing_id=unprocessed_officer.sfu_computing_id).first() is None
        )
        unprocessed_officer.number_of_nags += 1
        unprocessed_officer.save()
        if (unprocessed_officer.number_of_nags % 3) == 0:
            send_discord_dm(
                '288148680479997963', "unfilled in officer data",
                f"{unprocessed_officer.full_name} still has not filled in their data..."
            )
        logger.info(
            f"[about/nag_officers_to_enter_info.py()] {'nagged ' if success else 'was not able to nag '}"
            f"{unprocessed_officer.full_name} to fill in their info"
            f"{'' if success else f' due to error {error_message}'}."
        )
