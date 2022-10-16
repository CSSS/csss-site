from django.db import models


class CronJob(models.Model):
    job_name = models.CharField(
        max_length=5000
    )
    schedule = models.CharField(
        max_length=500
    )
