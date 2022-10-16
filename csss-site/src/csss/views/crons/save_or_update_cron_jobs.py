from csss.models import CronJob


def save_or_update_cron_jobs(cron_jobs, draft_cron_jobs):
    for (job_name, cron_job) in cron_jobs.items():
        if draft_cron_jobs[job_name] == "":
            cron_jobs[job_name].delete()
        else:
            cron_jobs[job_name].schedule = draft_cron_jobs[job_name]
    for (job_name, schedule) in draft_cron_jobs.items():
        if schedule != "":
            CronJob(job_name=job_name, schedule=schedule).save()
