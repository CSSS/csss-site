# Generated by Django 2.2.28 on 2023-07-06 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csss', '0007_cssserror_file_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='cssserror',
            name='fixed',
            field=models.BooleanField(default=False),
        ),
    ]
