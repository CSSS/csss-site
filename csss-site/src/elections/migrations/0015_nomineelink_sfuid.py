# Generated by Django 2.2.27 on 2023-03-11 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0014_auto_20230301_1908'),
    ]

    operations = [
        migrations.AddField(
            model_name='nomineelink',
            name='sfuid',
            field=models.CharField(default=None, max_length=8, null=True),
        ),
    ]
