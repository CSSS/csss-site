# Generated by Django 2.2.27 on 2022-04-04 15:02

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('about', '0009_auto_20220323_1950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='term',
            name='term',
            field=models.CharField(choices=[('Spring', 'Spring'), ('Summer', 'Summer'), ('Fall', 'Fall')], default='Fall', max_length=6),
        ),
        migrations.AlterField(
            model_name='term',
            name='year',
            field=models.IntegerField(default='2022'),
        ),
        migrations.CreateModel(
            name='NewOfficer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discord_id', models.CharField(max_length=20)),
                ('sfu_computing_id', models.CharField(max_length=10)),
                ('full_name', models.CharField(default='NA', max_length=100)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('position_name', models.CharField(default='President', max_length=300)),
                ('re_use_start_date', models.BooleanField(default=True)),
                ('overwrite_current_officer', models.BooleanField(default=False)),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='about.Term')),
            ],
        ),
    ]
