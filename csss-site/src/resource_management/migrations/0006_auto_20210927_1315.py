# Generated by Django 2.2.13 on 2021-09-27 13:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resource_management', '0005_auto_20210121_1826'),
    ]

    operations = [
        migrations.RenameField(
            model_name='processnewofficer',
            old_name='new_start_date',
            new_name='use_new_start_date',
        ),
    ]
