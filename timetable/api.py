import os
from typing import Set
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.models import User
import datetime
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import (
    MethodNotAllowed,
    AuthenticationFailed,
    PermissionDenied,
)
from django.http import FileResponse, HttpResponse
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action
from core.models import Course, Department, Staff, Venue
from core.serializers import (
    CourseSerializer,
    DepartmentSerializer,
    StaffSerializer,
    VenueSerializer,
)
from timetable.forms import (
    AddSlotCourseForm,
    AddTimetableForm,
    NewComplainForm,
    NewComplainMessageForm,
    TimetableConfigurationForm,
    UpdateSlotCourse,
)

from timetable.qeueing import Queue, each

from timetable.models import (
    Complain,
    ComplainMessage,
    SlotCourse,
    Timetable,
    TimetableSlot,
    assign_invigilator,
    slot_courses,
)
from timetable.serializers import (
    ComplainMessageSerializer,
    CreatedTimetableSerializer,
    MinimalTimetableSlotSeriallizer,
    complainSerializer,
    SlotCourseSeriallizer,
    TimetableSerializer,
    TimetableSlotSeriallizer,
)

from rest_framework.permissions import IsAuthenticated, AllowAny
from account.permissions import userIsAdmin, IsAdmin, userIsStaff, userIsStudent


class TimetableViewSet(ViewSet):
    def list(self, request: Request):
        if userIsAdmin(request):
            tables = Timetable.objects.all()
        else:
            tables = Timetable.objects.filter(is_current=True)

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
        elif request_method == "DELETE":
            if not userIsAdmin(request):
                raise PermissionDenied("Only admin users can delete timetables")

            timetables = Timetable.objects.filter(Q(pk__in=timetable_pks))
            timetables.delete()
            return Response(TimetableSerializer(timetables, many=True).data)
        else:
            raise MethodNotAllowed(method=request_method)

    def create(self, request: Request):
        if not userIsAdmin(request):
            raise PermissionDenied("Only admin users can create timetable")
        with transaction.atomic():
            form = AddTimetableForm(request.data)  # type: ignore
            if not form.is_valid():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "details": "Invalid form was provided",
                        "errors": form.errors,
                    },
                )
            timetable: Timetable = form.save(commit=False)
            timetable.created_on = datetime.datetime.now()
            timetable.start_date = datetime.datetime.today()
            timetable.end_date = datetime.datetime.today()
            timetable.save()

            # timetable = Timetable.objects.get(pk = timetable.pk)

            return Response(CreatedTimetableSerializer(timetable).data)

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

    @action(detail=True, methods=["GET"])
    def courses_by_slot_course(self, request: Request, pk=None):
        """
        Provides the list of a timetable courses, using the pk of the timetable slot course to
        locate the timetale
        """

        try:
            slot_course = SlotCourse.objects.get(pk=pk)
            timetable = slot_course.slot.timetable

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

    @action(
        detail=True, methods=("POST",), permission_classes=(IsAuthenticated, IsAdmin)
    )
    def configuration(self, request: Request, pk=None):
        """Route for getting and updating a timetable configuration

        Args:
            request (Request): A DRF request object
            pk (number, optional): The pk of the timetable. Defaults to None.

        Returns:
            200: If the update was successfull, and request type is POST
        """

        try:
            timetable = Timetable.objects.get(pk=pk)
            form = TimetableConfigurationForm(request.data)  # type: ignore

            if not form.is_valid():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"details": "Invalid form provided", "errors": form.errors},
                )

            data: Timetable = form.save(commit=False)

            timetable.slot_per_day = data.slot_per_day
            timetable.start_date = data.start_date
            timetable.end_date = data.end_date
            timetable.excluded_days = data.excluded_days or []
            timetable.excluded_week_days = data.excluded_week_days or []

            timetable.save()

            return Response(TimetableSerializer(timetable).data)

        except Timetable.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable not found"},
            )

    @action(detail=True, methods=["GET"])
    def slots(self, request: Request, pk=None):
        try:
            timetable = Timetable.objects.get(pk=pk)
            slots = TimetableSlot.objects.filter(timetable=timetable.pk).order_by(
                "index"
            )

            return Response(MinimalTimetableSlotSeriallizer(slots, many=True).data)
        except Timetable.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable not found"},
            )

    @action(detail=True, methods=["GET"])
    def slot(self, request: Request, pk=None):
        try:
            slot = TimetableSlot.objects.get(pk=pk)
            return Response(
                TimetableSlotSeriallizer(
                    slot,
                ).data
            )
        except Timetable.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable slot not found"},
            )

    @action(detail=True, methods=["GET"])
    def slots_departments(self, request: Request, pk=None):
        slots_id = request.query_params.getlist("slots", default=[])

        departments: Set[Department] = set()

        try:
            timetable = Timetable.objects.get(pk=pk)
            slots = TimetableSlot.objects.filter(Q(pk__in=slots_id))

            for slot in slots:
                courses = slot.courses.all()
                for course in courses:
                    departments.update(course.course.departments.all())

            return Response(
                DepartmentSerializer(
                    departments,
                    many=True,
                ).data
            )
        except Timetable.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable slot not found"},
            )

    @action(detail=True)
    def day_slots(self, request: Request, pk=None):
        try:
            day = int(request.query_params.get("day", 0))
            if day < 1:
                raise ValueError("Day not and integer greather than 0")
            timetable = Timetable.objects.get(pk=pk)

            slots = TimetableSlot.objects.filter(
                timetable=timetable.pk, day=day
            ).order_by("index")
            return Response(TimetableSlotSeriallizer(slots, many=True).data)

        except Timetable.DoesNotExist as e:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable does not exist", "errors": str(e)},
            )
        except ValueError as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": "Invalid day provided", "errors": str(e)},
            )
        except TypeError as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": "Invalid day provided", "errors": str(e)},
            )

    @action(detail=True)
    def slot_available_venues(self, request: Request, pk=None):
        try:
            course_slot = SlotCourse.objects.get(pk=pk)
            slot = course_slot.slot
            timetable = slot.timetable

            venues = set(timetable.venues.all())
            adjacent_slots = TimetableSlot.objects.filter(
                index__in=[slot.index - 1, slot.index + 1], day=slot.day
            )
            adjacent_slots_id: list[int] = list(
                map(lambda adjacent_slot: adjacent_slot.pk, adjacent_slots)
            )

            adjacent_slot_courses = SlotCourse.objects.filter(
                slot__in=adjacent_slots_id
            )
            used_venues = set([])
            each(
                lambda course: used_venues.update(course.venues.all()),
                adjacent_slot_courses,
            )

            slot_courses = SlotCourse.objects.filter(
                slot=slot.pk,
            ).exclude(pk=pk)
            each(lambda course: used_venues.update(course.venues.all()), slot_courses)

            available_venues = set(course_slot.venues.all())
            available_venues.update((venues - used_venues))

            return Response(VenueSerializer(available_venues, many=True).data)

        except TimetableSlot.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "No course slot was found"},
            )

    @action(detail=True)
    def slot_available_staffs(self, request: Request, pk=None):
        """Returns the list of staffs that are not assigned
        as invigilators in the adjacent slots to the slot of the current SlotCourse with id = pk

        Args:
            pk (int, optional): The id of the current slot course. Defaults to None.

        Returns:
            404 : if course slot does not exist
            200 : list of staffs
        """
        try:
            course_slot = SlotCourse.objects.get(pk=pk)
            slot = course_slot.slot
            timetable = slot.timetable

            staffs = set(timetable.staffs.all())
            adjacent_slots = TimetableSlot.objects.filter(
                index__in=[slot.index - 1, slot.index + 1], day=slot.day
            )
            adjacent_slots_id: list[int] = list(
                map(lambda adjacent_slot: adjacent_slot.pk, adjacent_slots)
            )

            adjacent_slot_courses = SlotCourse.objects.filter(
                slot__in=adjacent_slots_id
            )
            assigned_staffs: set[Staff] = set([])
            each(
                lambda course: assigned_staffs.update(course.invigilators.all()),
                adjacent_slot_courses,
            )

            slot_courses = SlotCourse.objects.filter(
                slot=slot.pk,
            ).exclude(pk=pk)
            each(
                lambda course: assigned_staffs.update(course.invigilators.all()),
                slot_courses,
            )

            free_staffs = set(course_slot.invigilators.all())
            free_staffs.update((staffs - assigned_staffs))

            return Response(StaffSerializer(free_staffs, many=True).data)

        except TimetableSlot.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "No course slot was found"},
            )

    @action(
        detail=True, methods=["POST"], permission_classes=(IsAuthenticated, IsAdmin)
    )
    def update_slot_course(self, request: Request, pk=None):
        """Updates a timetable slot course with id of pk

        Args:
            request (Request): _description_
            pk (_type_, optional): _description_. Defaults to None.

        Returns:
            400 : Invalid form provided
            404 : SlotCourse not found
            200 : Update was successful
        """

        try:
            course_slot = SlotCourse.objects.get(pk=pk)
            form = UpdateSlotCourse(data=request.data)  # type: ignore

            if not form.is_valid():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"details": "Invalid form provided", "errors": form.errors},
                )

            data = form.cleaned_data

            venues = Venue.objects.filter(
                pk__in=set(map(lambda id: int(id), data["venues"]))
            )
            invigilators = Staff.objects.filter(
                pk__in=set(map(lambda id: int(id), data["invigilators"]))
            )
            supervisor = Staff.objects.get(pk=int(data["supervisor"]))

            course_slot.venues.set(venues)
            course_slot.invigilators.set(invigilators)
            course_slot.supervisor = supervisor

            course_slot.save()

            return Response(SlotCourseSeriallizer(course_slot).data)

        except SlotCourse.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Slot course was not found"},
            )

    @action(
        detail=True, methods=["DELETE"], permission_classes=(IsAuthenticated, IsAdmin)
    )
    def slot_course(self, request: Request, pk=None):
        """Handles deleting of course slot

        Args:
            request (Request): _description_
            pk (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        try:
            course_slot = SlotCourse.objects.get(pk=pk)
            timetable = course_slot.slot.timetable

            method = request._request.method

            if method == "DELETE":
                # TODO handle deletion of slot course
                course_slot.delete()
                return Response({"details": "Slot course deleted"})

            return Response(
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
                data={"details": "Method handler not implemented yet"},
            )
        except SlotCourse.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Slot course does not exist in database"},
            )

    @action(
        detail=True, methods=["POST"], permission_classes=(IsAuthenticated, IsAdmin)
    )
    def add_slot_course(self, request: Request, pk=None):
        """Adds a new slot course to the slot with id = pk

        Args:
            request (Request): _description_
            pk (_type_, optional): The id of the TimetableSlot

        Returns:
            _type_: _description_
        """

        try:
            slot = TimetableSlot.objects.get(pk=pk)

            form = AddSlotCourseForm(request.data)  # type: ignore

            if not form.is_valid():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"details": "Invalid form provided", "errors": form.errors},
                )

            slot_course: SlotCourse = form.save(commit=False)
            slot_course.slot = slot
            slot_course.save()

            return Response(
                SlotCourseSeriallizer(slot_course).data, status=status.HTTP_201_CREATED
            )

        except TimetableSlot.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable slot does not exist"},
            )

    @action(detail=True)
    def unassigned_courses(self, request: Request, pk=None):
        """Returns the list of courses that have not been alocated a slot yet

        Args:
            request (Request): _description_
            pk (_type_, optional): pk of the timetable

        Returns:
            404 : Timetable not found
        """
        try:
            timetable = Timetable.objects.get(pk=pk)

            assigned_courses_map = SlotCourse.objects.filter(
                slot__timetable=timetable.pk
            ).values("course")
            all_courses_pk = set(
                map(lambda entry: entry["pk"], timetable.courses.all().values("pk"))
            )
            assigned_courses_pk = set(
                map(lambda entry: entry["course"], assigned_courses_map)
            )

            unassigned = all_courses_pk - assigned_courses_pk

            unassigned_courses = Course.objects.filter(pk__in=unassigned)

            return Response(CourseSerializer(unassigned_courses, many=True).data)

        except Timetable.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable not found"},
            )

    @action(detail=True, permission_classes=(IsAuthenticated, IsAdmin))
    def generate(self, request: Request, pk=None):
        try:
            timetable = Timetable.objects.get(pk=pk)
            result = timetable.generate()
            timetable.auto_assign_invigilators()
            return Response(
                result
            )

        except Timetable.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"detail": "Timetable not fount"}
            )

    @action(
        detail=True, methods=("POST",), permission_classes=(IsAuthenticated, IsAdmin)
    )
    def auto_assign_invigilators(self, request: Request, pk=None):
        """Tries to assign invigilators to all the courses in the timetable"""
        try:
            timetable = Timetable.objects.get(pk=pk)
            (slots, unasigned_slots) = timetable.auto_assign_invigilators()
            return Response(TimetableSlotSeriallizer(slots, many=True).data)
        except TimetableSlot.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"details": "Slot not found"}
            )

    @action(
        detail=True, methods=("POST",), permission_classes=(IsAuthenticated, IsAdmin)
    )
    def auto_assign_venues(self, request: Request, pk=None):
        """Tries to assign venues to all the courses in a slot"""

        try:
            timetable = Timetable.objects.get(pk=pk)

            slots = TimetableSlot.objects.filter(timetable=timetable.pk)
            all_venues = set(timetable.venues.all())

            for slot in slots:
                if len(all_venues) == 0:
                    return Response(
                        status=status.HTTP_406_NOT_ACCEPTABLE,
                        data={"details": "No venues for timetable"},
                    )

                slot_courses = SlotCourse.objects.filter(slot=pk).order_by(
                    "course__student_count"
                )

                if len(slot_courses) == 0:
                    continue

                adjacent_slot_courses = SlotCourse.objects.filter(
                    slot__day=slot.day,
                ).exclude(pk=slot.pk)

                used_venues: set[Venue] = set()
                each(
                    lambda sCourse: used_venues.update(sCourse.venues.all()),
                    adjacent_slot_courses,
                )

                available_venues = set(slot.timetable.venues.all())
                # - used_venues

                if len(available_venues) < 1:
                    available_venues = set(slot.timetable.venues.all())

                for slot_course in slot_courses:
                    slot_course.auto_assign_venues(available_venues)
                    available_venues = available_venues - set(slot_course.venues.all())

            return Response(TimetableSlotSeriallizer(slots, many=True).data)
        except Timetable.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable does not exist"},
            )

    @action(detail=True, methods=("GET",), permission_classes=(AllowAny,))
    def dates(self, request: Request, pk=None):
        try:
            timetable = Timetable.objects.get(pk=pk)
            return Response(timetable.timetable_days())
        except Timetable.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable not found"},
            )
            
    @action(detail=True, methods=("GET",), permission_classes=(AllowAny,))
    def export(self, request:Request, pk = None):
        try:
            timetable = Timetable.objects.get(pk = pk)
            
            file = None
            if userIsAdmin(request):
                file = timetable.export_excel("admin")
            elif userIsStaff(request):
                file = timetable.export_excel("staff")
            else:
                file = timetable.export_excel()
                
            file.close()
            
            with open(file.name, "rb") as f:
                
                response = HttpResponse(f.read(), 
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers = {"Content-Disposition":f'attachment; filename="{timetable.title}".xlsx'} )
                
            os.unlink(file.name)
            
            return response
        
        except Timetable.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable not found"},
            )
        
    @action(detail=True, methods=("GET",), permission_classes=(AllowAny,))
    def set_current(self, request: Request, pk = None):
        
        try:
            timetable = Timetable.objects.get(pk = pk)
            Timetable.objects.filter(is_current = True).update(is_current = False)
            timetable.is_current = True 
            timetable.save()
            
            return Response(TimetableSerializer(timetable).data)
        
        except Timetable.DoesNotExist:
            return Response( status = status.HTTP_404_NOT_FOUND, data = {
                "details":"Timetable was not found"
            })

class SlotCourseViewSet(ViewSet):
    def retrieve(self, request: Request, pk=None):
        try:
            slot_course = SlotCourse.objects.get(pk=pk)
            return Response(SlotCourseSeriallizer(slot_course).data)
        except SlotCourse.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Slot course not found"},
            )

    def create(self, request: Request):
        """Adds a new slot course to the slot with id = pk

        Args:
            request (Request): _description_
            pk (_type_, optional): The id of the TimetableSlot

        Returns:
            _type_: _description_

        """

        if not userIsAdmin(request):
            raise PermissionDenied("Only admin user can add course to a timetable slot")

        try:
            form = AddSlotCourseForm(request.data)  # type: ignore

            if not form.is_valid():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"details": "Invalid form provided", "errors": form.errors},
                )

            slot_course: SlotCourse = form.save(commit=False)
            slot_course.save()

            return Response(
                SlotCourseSeriallizer(slot_course).data, status=status.HTTP_201_CREATED
            )

        except TimetableSlot.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable slot does not exist"},
            )

    def delete(self, request: Request, pk=None):
        """Handles deleting of course slot

        Args:
            request (Request): _description_
            pk (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """

        if not userIsAdmin(request):
            raise PermissionDenied(
                "Only admin user can delete course from a timetable slot"
            )
        try:
            course_slot = SlotCourse.objects.get(pk=pk)
            timetable = course_slot.slot.timetable

            method = request._request.method

            if method == "DELETE":
                # TODO handle deletion of slot course
                course_slot.delete()
                return Response({"details": "Slot course deleted"})

            return Response(
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
                data={"details": "Method handler not implemented yet"},
            )
        except SlotCourse.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Slot course does not exist in database"},
            )

    @action(
        detail=True, methods=("POST",), permission_classes=(IsAuthenticated, IsAdmin)
    )
    def auto_assign_venue(self, request: Request, pk=None):
        try:
            course_slot = SlotCourse.objects.get(pk=pk)
            course_slot.auto_assign_venues()
            return Response(SlotCourseSeriallizer(course_slot).data)
        except SlotCourse.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Slot course not found"},
            )

    @action(
        detail=True, methods=("POST",), permission_classes=(IsAuthenticated, IsAdmin)
    )
    def auto_assign_invigilator(self, Request: Request, pk=None):
        try:
            slot_course = SlotCourse.objects.get(pk=pk)
            # slot_course.auto_assign_invigilator()
            assign_invigilator(slot_course)
            return Response(SlotCourseSeriallizer(slot_course).data)
        except SlotCourse.NoStaffAvailable as e:
            return Response(
                status=status.HTTP_412_PRECONDITION_FAILED,
                data={"details": "No staff avaialble", "error": str(e)},
            )
        except SlotCourse.NoVenueAssigned as e:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data={"details": "No venue assigned", "error": str(e)},
            )
        except SlotCourse.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "SlotCourse does not exist"},
            )


class SlotViewSet(ViewSet):
    @action(
        detail=True, methods=("POST",), permission_classes=(IsAuthenticated, IsAdmin)
    )
    def auto_assign_venues(self, request: Request, pk=None):
        """Tries to assign venues to all the courses in a slot"""

        slot = TimetableSlot.objects.get(pk=pk)

        all_venues = set(slot.timetable.venues.all())

        if len(all_venues) == 0:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data={"details": "No venues for timetable"},
            )

        slot_courses = SlotCourse.objects.filter(slot=pk).order_by(
            "course__student_count"
        )

        if len(slot_courses) == 0:
            return Response(TimetableSlotSeriallizer(slot).data)

        adjacent_slot_courses = SlotCourse.objects.filter(
            slot__day=slot.day,
        ).exclude(pk=slot.pk)

        used_venues: set[Venue] = set()
        each(
            lambda sCourse: used_venues.update(sCourse.venues.all()),
            adjacent_slot_courses,
        )

        available_venues = set(slot.timetable.venues.all())
        # - used_venues

        if len(available_venues) < 1:
            available_venues = set(slot.timetable.venues.all())

        for slot_course in slot_courses:
            slot_course.auto_assign_venues(available_venues)
            available_venues = available_venues - set(slot_course.venues.all())

        return Response(TimetableSlotSeriallizer(slot).data)

    @action(
        detail=True, methods=("POST",), permission_classes=(IsAuthenticated, IsAdmin)
    )
    def auto_assign_invigilators(self, request: Request, pk=None):
        """Tries to assign invigilators to all the courses in a slot"""
        try:
            slot = TimetableSlot.objects.get(pk=pk)
            all_slot_courses = slot_courses([slot])

            unasigned_slot_courses: set[SlotCourse] = set()

            for slot_course in all_slot_courses:
                try:
                    assign_invigilator(slot_course)
                except SlotCourse.NoStaffAvailable:
                    unasigned_slot_courses.add(slot_course)

            return Response(TimetableSlotSeriallizer(slot).data)
        except TimetableSlot.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"details": "Slot not found"}
            )


class ComplainViewSet(ViewSet):
    def create(self, request: Request):
        # TODO Handle authentication of admin, student and staff
        try:
            form = NewComplainForm(request.data)  # type: ignore

            if not form.is_valid():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"details": "Invalid form provided", "errors": form.errors},
                )

            complain: Complain = form.save(commit=False)

            user: User = request.user
            # TODO Remove this condition only student and staff can create complain
            if not user.is_anonymous:
                complain.user = user

            print(form.cleaned_data)

            complain_message = ComplainMessage(complain=complain)
            complain_message.user = complain.user
            complain_message.message = form.cleaned_data["message"]

            complain.save()
            complain_message.save()

            return Response(
                status=status.HTTP_201_CREATED, data=complainSerializer(complain).data
            )

        except SlotCourse.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "No slot course was found"},
            )

    @action(detail=True)
    def level_courses(self, request: Request, pk=None):
        """Returns the list of courses on the same slot that belong to
        thesame level and department with the slot course course with id = pk

        Args:
            request (Request): _description_
            pk (_type_, optional): _description_. Defaults to None.
        """

        try:
            slot_course = SlotCourse.objects.get(pk=pk)
            similar_courses = SlotCourse.objects.filter(
                slot=slot_course.slot.pk, course__level=slot_course.course.level
            )
            matchies: set[SlotCourse] = set([])

            departments = set(slot_course.course.departments.all())

            for course in similar_courses:
                if course.course.department == slot_course.course.department:
                    matchies.add(course)
                    continue
                if course.course.departments.contains(slot_course.course.department):
                    matchies.add(course)

                similar_departments = set(course.course.departments.all())

                if len(departments.intersection(similar_departments)) > 0:
                    matchies.add(course)

            return Response(SlotCourseSeriallizer(matchies, many=True).data)
        except SlotCourse.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "No slot course found"},
            )

    @action(detail=True)
    def slot(self, request: Request, pk=None):
        """Returns the list of complain for a particular course slot

        Args:
            request (Request): _description_
            pk (_type_, optional): _description_. Defaults to None.
        """

        try:
            slot_course = SlotCourse.objects.get(pk=pk)
            complains = Complain.objects.filter(slot_course=slot_course)

            return Response(complainSerializer(complains, many=True).data)
        except SlotCourse.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Slot course not found"},
            )

    @action(detail=True, methods=("POST",))
    def message(self, request: Request, pk=None):
        """Post a new message to a complain

        Args:
            request (Request): _description_
            pk (_type_, optional): _description_. Defaults to None.
        """

        try:
            complain = Complain.objects.get(pk=pk)

            form = NewComplainMessageForm(request.data)  # type: ignore

            if not form.is_valid():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"details": "Invalid form provided", "errors": form.errors},
                )

            message: ComplainMessage = form.save(commit=False)

            user: User = request.user

            if not user.is_anonymous:
                message.user = user

            message.complain = complain
            message.save()

            return Response(ComplainMessageSerializer(message).data)
        except Complain.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Complain does not exist"},
            )

    @action(detail=True)
    def timetable(self, request: Request, pk=None):
        try:
            timetable = Timetable.objects.get(pk=pk)

            complains = Complain.objects.filter(
                slot_course__slot__timetable=timetable.pk
            )
            issues = []

            for complain in complains:
                issues.append(
                    {
                        # "course":CourseSerializer(complain.slot_course.course).data,
                        "slot_course": complain.slot_course.pk,
                        "type": complain.complain_type,
                        "related_course": CourseSerializer(complain.related_course).data
                        if complain.related_course
                        else None,
                        "related_slot_course": complain.related_slot_course.pk
                        if complain.related_slot_course
                        else None,
                        "heading": ComplainMessageSerializer(
                            complain.all_messages().first()
                        ).data,
                    }
                )

            return Response(issues)

        except Timetable.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Timetable not found"},
            )
