# Generated by Django 2.2.13 on 2021-06-06 21:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0009_auto_20210517_2331'),
    ]

    operations = [
        migrations.CreateModel(
            name='NomineeLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=140)),
                ('passphrase', models.CharField(max_length=300, null=True, unique=True)),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elections.Election')),
            ],
        ),
    ]
