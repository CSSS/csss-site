# Generated by Django 2.2.28 on 2022-09-03 23:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resource_management', '0016_remove_mediatobemoved_file_id'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GoogleDriveFileAwaitingOwnershipChange',
        ),
    ]
