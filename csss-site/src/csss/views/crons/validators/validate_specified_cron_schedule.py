from apscheduler.triggers.cron import CronTrigger


def validate_specified_cron_schedule(draft_cron_jobs):
    """
    Ensures that the user specified shedules work with the Crontrigger

    Keyword Arguments
    draft_cron_jobs -- the user updates for the cron jobs

    Return
    Boolean -- indicates whether the specified schedules are valid
    error_message -- the error message if the specified schedules are valid
    """
    for (job_name, specified_schedule) in draft_cron_jobs.items():
        if specified_schedule != "":
            try:
                CronTrigger.from_crontab(specified_schedule)
            except ValueError as e:
                return False, (
                    f"Invalid schedule specified for {job_name}: {e}<br>"
                    f"See <a target='_blank' href='https://en.wikipedia.org/wiki/Cron'>here</a> "
                    f"for more information on the format accepted here."
                )
    return True, None
