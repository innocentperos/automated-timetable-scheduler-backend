from django.contrib import admin

from timetable.models import Complain, Timetable, TimetableSlot, SlotCourse


# Register your models here.
@admin.register(Timetable)
class TimetableAdminModel(admin.ModelAdmin):
    list_display = ("id", "title", "duration", "slot_per_day", "courses_count", "is_current")

    @admin.display()
    def courses_count(self, model: Timetable):
        return model.courses.count()


@admin.register(TimetableSlot)
class TimetableSlotAdminModel(admin.ModelAdmin):
    list_display = ("id", "timetable", "index")


@admin.register(SlotCourse)
class SlotCourseAdminModel(admin.ModelAdmin):
    list_display = ("course", "slot", "supervisor",)

@admin.register(Complain)
class ComplainAdminModel(admin.ModelAdmin):
    list_display = ('slot_course','user','resolved',)
    