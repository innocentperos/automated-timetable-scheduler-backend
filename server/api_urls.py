from django.urls import path
from rest_framework.routers import DefaultRouter
from core.api import courses, CourseViewSet, DepartmentViewSet, VenueViewSet

from timetable.api import TimetableViewSet

urlpatterns = [
    path(
        "courses/",
        courses,
    )
]

router = DefaultRouter()
router.register("courses", CourseViewSet, basename="courses")
router.register("departments", DepartmentViewSet, basename="departments")
router.register("venues", VenueViewSet, basename="venues")

router.register("timetables", TimetableViewSet, basename="timetables")
