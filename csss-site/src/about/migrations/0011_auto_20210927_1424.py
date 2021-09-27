# Generated by Django 2.2.13 on 2021-09-27 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('about', '0010_auto_20210927_1420'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='officer',
            name='unique_officer_for_term',
        ),
        migrations.AddConstraint(
            model_name='officer',
            constraint=models.UniqueConstraint(fields=('position_name', 'name', 'elected_term__term_number', 'start_date'), name='unique_officer_for_term'),
        ),
    ]
