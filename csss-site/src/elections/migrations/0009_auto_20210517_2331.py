# Generated by Django 2.2.13 on 2021-05-17 23:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0008_auto_20210517_2330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nominee',
            name='election',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elections.Election'),
        ),
    ]
