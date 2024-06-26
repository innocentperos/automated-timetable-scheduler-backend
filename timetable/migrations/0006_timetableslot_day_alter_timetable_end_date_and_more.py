# Generated by Django 5.0 on 2024-02-17 05:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("timetable", "0005_alter_timetable_end_date_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="timetableslot",
            name="day",
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="timetable",
            name="end_date",
            field=models.DateField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name="timetable",
            name="start_date",
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]
