from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed

from core.forms import (
    AddCourseForm,
    AddDepartmentForm,
    AddVenueCategoryForm,
    AddVenueForm,
    AddStaffForm,
)

from core.models import Course, Department, Staff, Venue, VenueCategory
from core.serializers import (
    CourseSerializer,
    DepartmentSerializer,
    PlainCourseSerializer,
    PlainStaffSerializer,
    StaffSerializer,
    VenueCategorySerializer,
    VenueSerializer,
)


@api_view()
@csrf_exempt
def courses(request: Request):
    _courses = Course.objects.all()
    return Response(CourseSerializer(_courses, many=True).data)


class CourseViewSet(ViewSet):
    def list(self, request: Request):
        _courses = Course.objects.all()
        queries = request.query_params
        query = queries.get("q", None)
        if query:
            _courses = _courses.filter(
                Q(title__contains=query) | Q(code__contains=query)
            )
        return Response(CourseSerializer(_courses, many=True).data)

    def create(self, request: Request):
        form = AddCourseForm(request.data)  # type: ignore

        if not form.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "Invalid form was provided", "errors": form.errors},
            )

        course = form.save()

        return Response(
            status=status.HTTP_201_CREATED, data=CourseSerializer(course).data
        )

    @action(detail=False, methods=("POST", "DELETE"))
    def multiple(self, request: Request):
        request_method = request._request.method

        courses_pks: list[int] = request.data  # type: ignore

        if request_method == "POST":
            timetables = Course.objects.filter(Q(pk__in=courses_pks))
            return Response(CourseSerializer(timetables, many=True).data)
        elif request_method == "DETETE":
            timetables = Course.objects.filter(Q(pk__in=courses_pks))
            timetables.delete()
            return Response(CourseSerializer(timetables, many=True).data)
        else:
            raise MethodNotAllowed(method=request_method)

    @action(methods=("DELETE",), detail=False)
    def multiple_delete(self, request: Request):
        ids = request.data

        if not ids:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "details": "Invalid form",
                },
            )

        course = Course.objects.filter(pk__in=ids)
        course.delete()
        return Response(CourseSerializer(course, many=True).data)

    @action(detail=False)
    def get_by_code(self, request: Request):
        code = request.query_params.get("code", None)

        course = Course.objects.filter(Q(code__iexact=code))

        return Response(CourseSerializer(course, many=True).data)


class DepartmentViewSet(ViewSet):
    def list(self, request: Request):
        departments = Department.objects.all()
        queries = request.query_params
        query = queries.get("q", None)
        if query:
            departments = departments.filter(
                Q(title__contains=query) | Q(code__contains=query)
            )
        return Response(DepartmentSerializer(departments, many=True).data)

    def create(self, request: Request):
        form = AddDepartmentForm(request.data)  # type: ignore
        if not form.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "details": "Invalid form",
                    "errors": form.errors,
                    "fields": form.errors.keys(),
                },
            )

        department = form.save()
        return Response(DepartmentSerializer(department).data)

    def retrieve(self, request: Request, pk=None):
        try:
            department = Department.objects.get(pk=pk)
            staffs = Staff.objects.filter(department=department)
            courses = Course.objects.filter(department=department)
            return Response(
                {
                    **DepartmentSerializer(department).data,
                    "staffs": PlainStaffSerializer(staffs, many=True).data,
                    "courses": PlainCourseSerializer(courses, many=True).data,
                }
            )
        except Department.DoesNotExist:
            return Response(
                {"Details": "Department not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=("POST", "DELETE"))
    def multiple(self, request: Request):
        request_method = request._request.method

        departments_pks: list[int] = request.data  # type: ignore

        if request_method == "POST":
            timetables = Department.objects.filter(Q(pk__in=departments_pks))
            return Response(DepartmentSerializer(timetables, many=True).data)
        elif request_method == "DETETE":
            timetables = Department.objects.filter(Q(pk__in=departments_pks))
            timetables.delete()
            return Response(DepartmentSerializer(timetables, many=True).data)
        else:
            raise MethodNotAllowed(method=request_method)

    @action(methods=("DELETE",), detail=False)
    def multiple_delete(self, request: Request):
        ids = request.data

        if not ids:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "details": "Invalid form",
                },
            )

        departments = Department.objects.filter(pk__in=ids)
        departments.delete()
        return Response(DepartmentSerializer(departments, many=True).data)

    def delete(self, request: Request, pk=None):
        print("deleting")
        try:
            department = Department.objects.get(pk=pk)
            department.delete()
            return Response(DepartmentSerializer(department).data)
        except Department.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Department not found"},
            )

    @action(detail=False)
    def get_by_code(self, request: Request):
        code = request.query_params.get("code", None)
        departments = Department.objects.filter(Q(code__iexact=code))

        return Response(DepartmentSerializer(departments, many=True).data)

    @action(detail=True)
    def courses(self, request: Request, pk = None):
        try:
            department = Department.objects.get(pk=pk)
            courses = Course.objects.filter(department = department)
            return Response(CourseSerializer(courses, many = True).data)
        except Department.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Department not found"},
            )
    @action(detail=True)
    def staffs(self, request: Request, pk = None):
        try:
            department = Department.objects.get(pk=pk)
            staffs = Staff.objects.filter(department = department)
            return Response(StaffSerializer(staffs, many = True).data)
        except Department.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Department not found"},
            )

class VenueViewSet(ViewSet):
    def list(self, request: Request):
        venues = Venue.objects.all()
        query = request.query_params.get("q", None)
        if query:
            venues = venues.filter(Q(title__icontainx=query) | Q(code__icontains=query))

        return Response(VenueSerializer(venues, many=True).data)

    @action(methods=("GET", "POST", "DELETE"), detail=False)
    def categories(self, request: Request):
        if request._request.method == "DELETE":
            # Handles for deleting venue categories
            categories = VenueCategory.objects.filter(Q(pk__in=request.data))
            categories.delete()

            return Response(
                status=status.HTTP_202_ACCEPTED,
                data=VenueCategorySerializer(categories, many=True).data,
            )
        elif request._request.method == "POST":
            # Handles for adding new venue category
            form = AddVenueCategoryForm(request.data)  # type: ignore
            if not form.is_valid():
                # The form for creating a new venue category is invalid

                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"details": "Invalid form provided", "errors": form.errors},
                )
            category = VenueCategory(title=form.cleaned_data["title"])
            category.save()
            return Response(
                status=status.HTTP_201_CREATED,
                data=VenueCategorySerializer(category).data,
            )

        categories = VenueCategory.objects.all()
        query = request.query_params.get("q", None)

        if query:
            categories = categories.filter(Q(title__icontainx=query))

        return Response(VenueCategorySerializer(categories, many=True).data)

    def create(self, request: Request):
        """
        Handles creation of new venue
        """
        form = AddVenueForm(request.data)  # type: ignore

        if not form.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"details": "Invalid form provided", "errors": form.errors},
            )
        venue = form.save()
        return Response(
            status=status.HTTP_201_CREATED, data=VenueSerializer(venue).data
        )

    @action(detail=False, methods=("POST", "DELETE"))
    def multiple(self, request: Request):
        request_method = request._request.method

        venues_pk: list[int] = request.data  # type: ignore

        if request_method == "POST":
            timetables = Venue.objects.filter(Q(pk__in=venues_pk))
            return Response(VenueSerializer(timetables, many=True).data)
        elif request_method == "DETETE":
            timetables = Venue.objects.filter(Q(pk__in=venues_pk))
            timetables.delete()
            return Response(VenueSerializer(timetables, many=True).data)
        else:
            raise MethodNotAllowed(method=request_method)

    @action(methods=("DELETE",), detail=False)
    def multiple_delete(self, request: Request):
        """
        Handles deletion of multiple venues at a time
        """
        pks = request.data
        if not pks:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "details": "Invalid form provided",
                    "errors": {"pk": ["No pk provided"]},
                },
            )

        venues = Venue.objects.filter(Q(pk__in=pks))
        venues.delete()

        return Response(VenueSerializer(venues, many=True).data)


class StafftViewSet(ViewSet):
    def list(self, request: Request):
        staffs = Staff.objects.all()
        queries = request.query_params
        query = queries.get("q", None)
        if query:
            staffs = staffs.filter(Q(title__contains=query) | Q(code__contains=query))
        return Response(StaffSerializer(staffs, many=True).data)

    def create(self, request: Request):
        form = AddStaffForm(request.data)  # type: ignore
        if not form.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "details": "Invalid form",
                    "errors": form.errors,
                    "fields": form.errors.keys(),
                },
            )

        staff = form.save()
        return Response(StaffSerializer(staff).data)

    def retrieve(self, request: Request, pk=None):
        try:
            staff = Staff.objects.get(pk=pk)
            return Response(StaffSerializer(staff).data)
        except Staff.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"details": "Staff not found"}
            )

    @action(detail=False, methods=("POST", "DELETE"))
    def multiple(self, request: Request):
        request_method = request._request.method

        staffs_pks: list[int] = request.data  # type: ignore

        if request_method == "POST":
            staffs = Staff.objects.filter(Q(pk__in=staffs_pks))
            return Response(StaffSerializer(staffs, many=True).data)
        elif request_method == "DETETE":
            staffs = Staff.objects.filter(Q(pk__in=staffs_pks))
            staffs.delete()
            return Response(StaffSerializer(staffs, many=True).data)
        else:
            raise MethodNotAllowed(method=request_method)

    def delete(self, request: Request, pk=None):
        try:
            staff = Staff.objects.get(pk=pk)
            staff.delete()
            return Response(StaffSerializer(staff).data)
        except Staff.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Staff not found"},
            )

    @action(detail=False)
    def get_by_staff_id(self, request: Request):
        code = request.query_params.get("staff_id", None)
        staffs = Staff.objects.filter(Q(code__iexact=code))

        return Response(StaffSerializer(staffs, many=True).data)
