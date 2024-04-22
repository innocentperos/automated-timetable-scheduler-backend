from django.urls import path
from rest_framework.routers import DefaultRouter
from core.api import (
    StafftViewSet,
    CourseViewSet,
    DepartmentViewSet,
    VenueViewSet,
)

from timetable.api import (
    TimetableViewSet,
    SlotCourseViewSet,
    SlotViewSet,
    ComplainViewSet,
)

from account.api import (
    AccountViewset
)

urlpatterns = [
    
]

router = DefaultRouter()
router.register("courses", CourseViewSet, basename="courses")
router.register("departments", DepartmentViewSet, basename="departments")
router.register("venues", VenueViewSet, basename="venues")
router.register("staffs", StafftViewSet, basename="staffs")


router.register("timetables", TimetableViewSet, basename="timetables")
router.register("slot_courses", SlotCourseViewSet, basename="slot_Courses")
router.register("slots", SlotViewSet, basename="timetable_slots")

router.register("complains", ComplainViewSet, basename="complains")

router.register("accounts", AccountViewset, basename="accounts")