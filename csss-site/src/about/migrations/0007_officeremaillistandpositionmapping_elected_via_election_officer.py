# Generated by Django 2.2.13 on 2021-05-11 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('about', '0006_auto_20210119_1833'),
    ]

    operations = [
        migrations.AddField(
            model_name='officeremaillistandpositionmapping',
            name='elected_via_election_officer',
            field=models.BooleanField(default=False),
        ),
    ]
