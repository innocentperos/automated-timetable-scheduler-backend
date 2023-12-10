# Generated by Django 4.2 on 2023-12-10 08:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Timetable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_created=True)),
                ('title', models.CharField(blank=True, max_length=50, null=True)),
                ('duration', models.IntegerField(default=5)),
                ('slot_per_day', models.IntegerField(default=4)),
                ('is_current', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('courses', models.ManyToManyField(blank=True, to='core.course')),
                ('staffs', models.ManyToManyField(blank=True, to='core.staff')),
                ('venues', models.ManyToManyField(blank=True, to='core.venue')),
            ],
        ),
        migrations.CreateModel(
            name='TimetableSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField()),
                ('timetable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slots', to='timetable.timetable')),
            ],
            options={
                'verbose_name': 'Slot',
                'verbose_name_plural': 'Slots',
            },
        ),
        migrations.CreateModel(
            name='SlotCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.course')),
                ('invigilators', models.ManyToManyField(blank=True, related_name='invigilating', to='core.staff')),
                ('slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slot_courses', to='timetable.timetableslot')),
                ('supervisor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='supervising', to='core.staff')),
                ('venues', models.ManyToManyField(blank=True, to='core.venue')),
            ],
            options={
                'verbose_name': 'Slot Course',
                'verbose_name_plural': 'Slot Courses',
            },
        ),
    ]