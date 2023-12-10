from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action

from core.forms import (
    AddCourseForm,
    AddDepartmentForm,
    AddVenueCategoryForm,
    AddVenueForm,
)

from core.models import Course, Department, Venue, VenueCategory
from core.serializers import (
    CourseSerializer,
    DepartmentSerializer,
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
        return Response({"Details": "Hello"})

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
