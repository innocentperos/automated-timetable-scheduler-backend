# Generated by Django 5.0 on 2024-01-02 07:36

import timetable.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0003_timetable_end_date_timetable_excluded_days_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timetable',
            name='excluded_week_days',
            field=models.JSONField(default=timetable.models.default_excluded_week_days),
        ),
    ]
