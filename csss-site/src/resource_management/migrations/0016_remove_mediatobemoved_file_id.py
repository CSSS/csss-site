# Generated by Django 2.2.27 on 2022-09-03 02:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resource_management', '0015_mediatobemoved'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mediatobemoved',
            name='file_id',
        ),
    ]
