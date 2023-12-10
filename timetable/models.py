from django.db import models

from core.models import Course, Staff, Venue


# Create your models here.
class Timetable(models.Model):
    title = models.CharField(max_length=50, null=True, blank=True)
    duration = models.IntegerField(default=5, )
    slot_per_day = models.IntegerField(default=4)
    is_current = models.BooleanField(default=False)
    courses = models.ManyToManyField(Course, blank=True)
    staffs = models.ManyToManyField(Staff, blank=True)
    venues = models.ManyToManyField(Venue, blank=True)
    created_on = models.DateTimeField(auto_created=True)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def slot_size(self):
        return self.duration * self.slot_per_day

    def __str__(self):
        return self.title


class TimetableSlot(models.Model):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name="slots")
    index = models.IntegerField()

    class Meta:
        verbose_name_plural = "Slots"
        verbose_name = "Slot"

    def __str__(self):
        return f"{self.timetable} ({self.index})"


class SlotCourse(models.Model):
    slot = models.ForeignKey(TimetableSlot, on_delete=models.CASCADE, related_name="slot_courses")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(Staff, null=True, on_delete=models.SET_NULL, related_name="supervising")
    invigilators = models.ManyToManyField(Staff, blank=True, related_name="invigilating")
    venues = models.ManyToManyField(Venue, blank=True)

    class Meta:
        verbose_name_plural = "Slot Courses"
        verbose_name = "Slot Course"

    def __str__(self):
        return f"{self.course} {self.slot}"
