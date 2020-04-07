from django.db import models


class OfficerUpdatePassphrase(models.Model):

    passphrase = models.CharField(
        max_length=300,
        primary_key=True,
    )
    used = models.BooleanField(
        default=False,
    )


class GDriveUsers(models.Model):
    gmail = models.CharField(
        max_length=300
    )
    name = models.CharField(
        max_length=300
    )
    file_id = models.CharField(
        max_length=5000
    )

class GDrivePublicFiles(models.Model):
    file_id = models.CharField(
        primary_key=True,
        max_length=5000
    )
    link = models.CharField(
        max_length=5000
    )
