from django.db import models


class CronJob(models.Model):
    job_name = models.CharField(
        max_length=5000,
        unique=True
    )
    schedule = models.CharField(
        max_length=500
    )

    def __str__(self):
        return f"Job {self.job_name} with schedule {self.schedule}"
