# Generated by Django 2.2.27 on 2023-04-12 01:42

import csss.PSTDateTimeField
from django.db import migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('csss', '0005_cssserror_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cronjob',
            name='last_update',
            field=csss.PSTDateTimeField.PSTDateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='cronjobrunstat',
            name='run_date',
            field=csss.PSTDateTimeField.PSTDateTimeField(default=django.utils.timezone.now),
        ),
    ]
