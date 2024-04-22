# Generated by Django 5.0 on 2024-01-02 07:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0002_timetable_semester_timetable_session'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetable',
            name='end_date',
            field=models.DateField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='timetable',
            name='excluded_days',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='timetable',
            name='excluded_week_days',
            field=models.JSONField(default=[0]),
        ),
        migrations.AddField(
            model_name='timetable',
            name='start_date',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]
