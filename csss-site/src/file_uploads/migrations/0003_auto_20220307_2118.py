# Generated by Django 2.2.24 on 2022-03-07 21:18

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file_uploads', '0002_auto_20201001_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfile',
            name='input_file',
            field=models.FileField(max_length=255, storage=django.core.files.storage.FileSystemStorage(location='/media/jace/jace_usb_1/1_CSSS/1_csss-site/media_root/'), upload_to='form_uploads/form_uploads/multiFileUploads/'),
        ),
    ]
