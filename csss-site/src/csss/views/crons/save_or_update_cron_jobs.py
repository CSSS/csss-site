from csss.models import CronJob


def save_or_update_cron_jobs(current_cron_jobs, draft_cron_jobs):
    for (job_name, cron_job) in current_cron_jobs.items():
        if draft_cron_jobs[job_name] == "":
            cron_job.delete()
            del draft_cron_jobs[job_name]
        else:
            cron_job.schedule = draft_cron_jobs[job_name]
            cron_job.save()
            del draft_cron_jobs[job_name]

    new_cron_jobs_to_save = {
        job_name: schedule
        for (job_name, schedule) in draft_cron_jobs.items()
        if schedule != ""
    }
    for (job_name, schedule) in new_cron_jobs_to_save.items():
        CronJob(job_name=job_name, schedule=schedule).save()
