from django.db import models


class OfficerUpdatePassphrase(models.Model):

    passphrase = models.CharField(
        max_length=300,
        primary_key=True,
    )
    used = models.BooleanField(
        default=False,
    )
