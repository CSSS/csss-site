# Generated by Django 2.2.13 on 2021-04-06 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0005_auto_20201216_1838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nominee',
            name='speech',
            field=models.CharField(max_length=30000),
        ),
    ]