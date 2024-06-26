# Generated by Django 5.0 on 2024-02-26 19:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("timetable", "0006_timetableslot_day_alter_timetable_end_date_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Complain",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("user_id", models.CharField(blank=True, max_length=50)),
                ("messages", models.JSONField(blank=True, default=list)),
                ("resolved", models.BooleanField(default=False)),
                (
                    "slot_course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="complains",
                        to="timetable.slotcourse",
                    ),
                ),
            ],
        ),
    ]
