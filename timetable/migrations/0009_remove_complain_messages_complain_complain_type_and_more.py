# Generated by Django 5.0 on 2024-03-01 06:38

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("timetable", "0008_remove_complain_user_id_complain_user"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="complain",
            name="messages",
        ),
        migrations.AddField(
            model_name="complain",
            name="complain_type",
            field=models.CharField(
                choices=[
                    ("level-conflict", "Level course conflict"),
                    ("other-confilct", "Other confilct"),
                ],
                default="other-confilct",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="complain",
            name="related_slot_course",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="timetable.slotcourse",
            ),
        ),
        migrations.AddField(
            model_name="complain",
            name="time",
            field=models.DateTimeField(
                auto_created=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="ComplainMessage",
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
                ("time", models.DateTimeField(auto_created=True)),
                ("message", models.TextField(blank=True)),
                (
                    "complain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="timetable.complain",
                    ),
                ),
                (
                    "reply_to",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="replies",
                        to="timetable.complainmessage",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
