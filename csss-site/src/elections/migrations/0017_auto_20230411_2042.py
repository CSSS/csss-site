# Generated by Django 2.2.27 on 2023-04-12 01:42

import csss.PSTDateTimeField
import datetime
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0016_nomineelink_discord_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='date',
            field=csss.PSTDateTimeField.PSTDateTimeField(default=datetime.datetime.now, verbose_name='Date to be made Public'),
        ),
    ]