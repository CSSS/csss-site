import datetime


def save_or_update_cron_jobs(saved_cron_jobs_dict, draft_cron_jobs):
    """
    Updates the saved Cron Jobs with the new schedules

    Keyword Arguments
    saved_cron_jobs_dict -- a dictionary of the saved CronJobs where the key is the name and the value is the
     CronJob object itself
    draft_cron_jobs -- the user updates for the cron jobs
    """
    for (job_name, cron_job) in saved_cron_jobs_dict.items():
        if cron_job.schedule != draft_cron_jobs[job_name]:
            cron_job.schedule = draft_cron_jobs[job_name]
            cron_job.last_update = datetime.datetime.now(date_timezone)
            cron_job.save()
        del draft_cron_jobs[job_name]

    # the below code will become relevant when I add a way to add a cron_job via the website
    # for now I am lazy and will revert to adding new jobs via the CRON_JOB_MAPPING dictionary
    # new_cron_jobs_to_save = {
    #     job_name: schedule
    #     for (job_name, schedule) in draft_cron_jobs.items()
    #     if schedule != ""
    # }
    # for (job_name, schedule) in new_cron_jobs_to_save.items():
    #     CronJob(job_name=job_name, schedule=schedule).save()
