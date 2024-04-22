from django.contrib import admin

from core.models import Department, Course, VenueCategory, Venue, Staff


# Register your models here.

@admin.register(Department)
class DepartmentAdminModel(admin.ModelAdmin):
    list_display = ("id", "title", "code")


@admin.register(Course)
class CourseAdminModel(admin.ModelAdmin):
    list_display = ("id", "title", "code", "level", "student_count", "shared")
    
    filter_horizontal = ["departments"]
    filter_vertical =["departments"]
    list_filter =["level","semester","departments"]

    @admin.display(boolean=True, )
    def shared(self, model: Course):
        return model.departments.count() > 1


@admin.register(VenueCategory)
class VenueCategoryAdminModel(admin.ModelAdmin):
    list_display = ("id", "title")


@admin.register(Venue)
class VenueAdminModel(admin.ModelAdmin):
    list_display = ("id", "title", "code", "capacity", "category")


@admin.register(Staff)
class StaffAdminModel(admin.ModelAdmin):
    list_display = ("id", "name", "department", "staff_id", "can_supervise", "can_invigilate")
