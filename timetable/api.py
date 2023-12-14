from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import datetime_safe
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action
from core.models import Course, Staff, Venue
from core.serializers import CourseSerializer, StaffSerializer, VenueSerializer
from timetable.forms import AddTimetableForm

from timetable.models import Timetable
from timetable.serializers import TimetableSerializer


class TimetableViewSet(ViewSet):
    def list(self, request: Request):
        tables = Timetable.objects.all()

        return Response(TimetableSerializer(tables, many=True).data)

    def retrieve(self, request: Request, pk=None):
        try:
            timetable = Timetable.objects.get(pk=pk)
            return Response(TimetableSerializer(timetable).data)
        except Timetable.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={
                    "details": "Timetable not found",
                },
            )

    @action(detail=False, methods=("POST", "DELETE"))
    def multiple(self, request: Request):
        request_method = request._request.method

        timetable_pks: list[int] = request.data  # type: ignore

        if request_method == "POST":
            timetables = Timetable.objects.filter(Q(pk__in=timetable_pks))
            return Response(TimetableSerializer(timetables, many=True).data)
        elif request_method == "DETETE":
            timetables = Timetable.objects.filter(Q(pk__in=timetable_pks))
            timetables.delete()
            return Response(TimetableSerializer(timetables, many=True).data)
        else:
            raise MethodNotAllowed(method=request_method)

    def create(self, request: Request):
        form = AddTimetableForm(request.data)  # type: ignore
        if not form.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": "Invalid form was provided", "errors": form.errors},
            )
        timetable: Timetable = form.save(commit=False)
        timetable.created_on = datetime_safe.datetime.now()
        timetable.save()

        return Response(TimetableSerializer(timetable).data)

    @action(detail=True, methods=["POST", "GET", "DELETE"])
    def courses(self, request: Request, pk=None):
        """
        Route for handling listing, adding and deleting courses from a table
        """

        try:
            timetable = Timetable.objects.get(pk=pk)
            request_method = request._request.method

            if request_method == "DELETE":
                courses_pk: list[int] = request.data  # type: ignore
                courses_to_remove = Course.objects.filter(Q(pk__in=courses_pk))

                for course in courses_to_remove:
                    timetable.courses.remove(course)

                return Response(CourseSerializer(courses_to_remove, many=True).data)

            elif request_method == "POST":
                courses_pk: list[int] = request.data  # type: ignore
                courses_to_add = Course.objects.filter(Q(pk__in=courses_pk))

                for course in courses_to_add:
                    timetable.courses.add(course)

                return Response(CourseSerializer(courses_to_add, many=True).data)
            else:
                courses = timetable.courses.filter()
                return Response(CourseSerializer(courses, many=True).data)

        except Timetable.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable not found"},
            )

    @action(detail=True, methods=["POST", "GET", "DELETE"])
    def venues(self, request: Request, pk=None):
        """
        Route for handling listing, adding and deleting venues from a table
        """

        try:
            timetable = Timetable.objects.get(pk=pk)
            request_method = request._request.method

            if request_method == "DELETE":
                venue_pks: list[int] = request.data  # type: ignore
                venues_to_remove = Venue.objects.filter(Q(pk__in=venue_pks))

                for venue in venues_to_remove:
                    timetable.venues.remove(venue)

                return Response(VenueSerializer(venues_to_remove, many=True).data)

            elif request_method == "POST":
                venue_pks: list[int] = request.data  # type: ignore
                venues_to_add = Venue.objects.filter(Q(pk__in=venue_pks))

                for venue in venues_to_add:
                    timetable.venues.add(venue)

                return Response(VenueSerializer(venues_to_add, many=True).data)
            else:
                venues = timetable.venues.filter()
                return Response(VenueSerializer(venues, many=True).data)

        except Timetable.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable not found"},
            )

    @action(detail=True, methods=["POST", "GET", "DELETE"])
    def staffs(self, request: Request, pk=None):
        """
        Route for handling listing, adding and deleting staffs from a table
        """

        try:
            timetable = Timetable.objects.get(pk=pk)
            request_method = request._request.method

            if request_method == "DELETE":
                staffs_pks: list[int] = request.data  # type: ignore
                staff_to_remove = Staff.objects.filter(Q(pk__in=staffs_pks))

                for staff in staff_to_remove:
                    timetable.staffs.remove(staff)

                return Response(StaffSerializer(staff_to_remove, many=True).data)

            elif request_method == "POST":
                staffs_pks: list[int] = request.data  # type: ignore
                staffs_to_add = Staff.objects.filter(Q(pk__in=staffs_pks))

                for venue in staffs_to_add:
                    timetable.staffs.add(venue)

                return Response(StaffSerializer(staffs_to_add, many=True).data)
            else:
                staffs = timetable.staffs.filter()
                return Response(StaffSerializer(staffs, many=True).data)

        except Timetable.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable not found"},
            )
