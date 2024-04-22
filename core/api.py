from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
import random

from core.forms import (
    AddCourseForm,
    UpdateCourseForm,
    AddDepartmentForm,
    AddVenueCategoryForm,
    AddVenueForm,
    AddStaffForm,
    UpdateStaffForm,
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

from account.permissions import (
    IsAdmin,
    IsStaff,
    IsStudent,
    userIsAdmin,
    userIsStaff,
    userIsStudent,
)
from rest_framework.permissions import IsAuthenticated


class CourseViewSet(ViewSet):
    def list(self, request: Request):
        """Returns the list off all the courses in the system"""

        _courses = Course.objects.all()
        queries = request.query_params
        query = queries.get("q", None)
        if query:
            _courses = _courses.filter(
                Q(title__contains=query) | Q(code__contains=query)
            )
        return Response(CourseSerializer(_courses, many=True).data)

    def create(self, request: Request):
        """Accept a valid form to create a new course

        Args:
            request (Request): _description_

        Returns:
            _type_: _description_
        """

        if not userIsAdmin(request):
            raise PermissionDenied("Only admin user can create new courses")

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

    def update(self, request: Request, pk: None):
        if not userIsAdmin(request):
            raise PermissionDenied("Only admin users can update courses")

        try:
            course = Course.objects.get(pk=pk)

            form = UpdateCourseForm(request.data)  # type: ignore

            if not form.is_valid():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"details": "Invalid form provided", "errors": form.errors},
                )

            data = form.cleaned_data

            used_code = (
                Course.objects.filter(code=data["code"]).exclude(pk=pk).count() > 0
            )

            if used_code:
                return Response(
                    status=status.HTTP_409_CONFLICT,
                    data={"details": "Code been used by another course"},
                )

            course.title = data["title"]
            course.code = data["code"]
            course.department = data["department"]
            course.departments.set(data["departments"])
            course.student_count = data["student_count"]
            course.level = data["level"]
            course.semester = data["semester"]
            course.save()

            return Response(CourseSerializer(course).data)

        except Course.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"details": "No course found"}
            )

    def retrieve(self, request: Request, pk=None):
        try:
            course = Course.objects.get(pk=pk)
            return Response(CourseSerializer(course).data)
        except Course.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Course does not exist"},
            )

    @action(
        detail=False,
        methods=("POST", "DELETE"),
        permission_classes=(IsAuthenticated, IsAdmin),
    )
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

    @action(
        methods=("DELETE",), detail=False, permission_classes=(IsAuthenticated, IsAdmin)
    )
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

    @action(detail=False, permission_classes=(IsAuthenticated, IsAdmin))
    def generate_random_courses(self, request: Request):
        levels = [100, 200, 300, 400]
        try:
            count: int = int(request.query_params.get("count", 0))
            department_max: int = int(request.query_params.get("department_max", 0))
            level: int = int(request.query_params.get("level", 0))
            semester: int = int(request.query_params.get("semester", 1))

            if count < 1 or department_max < 0:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "detail": "count and department max needs to be greather than 0"
                    },
                )
            if level not in levels:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"detail": "Invalid level"},
                )

            departments = set(Department.objects.all())
            department_count = len(departments)
            department_courses_count = {}
            completed_departments = set([])

            courses_added = []

            for current_index in range(count):
                pool = departments.difference(completed_departments)
                print(f"Index : {current_index}, Pool Size : {len(pool)}")

                if len(pool) == 0:
                    break

                else:
                    department = random.choice(list(pool))

                    if department not in department_courses_count:
                        department_courses_count[department] = 0

                    course = Course()
                    course.title = f"Course {current_index + 1}"
                    course.code = (
                        f"{department.code}{random.randrange(level+1, level+99)}"
                    )
                    course.department = department
                    course.level = level
                    course.semester = semester
                    course.student_count = random.randint(30, 300)
                    selected_departments = set()

                    if course.code.endswith("101") or random.randint(1, 30) % 8 == 0:
                        # Is a shared course
                        shared_department_count = random.randint(1, department_count)
                        selected_departments = set(
                            random.choices(list(departments), k=shared_department_count)
                        )
                        selected_departments = selected_departments.difference(
                            completed_departments
                        )

                    selected_departments.add(department)
                    try:
                        course.save()
                        course.departments.set(selected_departments)
                        course.save()
                        department_courses_count[department] = (
                            department_courses_count[department] + 1
                        )
                        courses_added.append(course)

                        if department_courses_count[department] >= department_max:
                            completed_departments.add(department)
                    except Exception:
                        pass

            return Response(
                data={
                    "detail": f"Added {len(courses_added)} courses",
                    "count": count,
                    "courses": PlainCourseSerializer(courses_added, many=True).data,
                }
            )

        except TypeError as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "wrong, missing or invalid count"},
            )
        except ValueError as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "missing or invalid count", "extra": str(e)},
            )


class DepartmentViewSet(ViewSet):
    def list(self, request: Request):
        """Returns list of departments in the system

        Args:
            request (Request): _description_

        Returns:
            _type_: _description_
        """
        departments = Department.objects.all()
        queries = request.query_params
        query = queries.get("q", None)
        if query:
            departments = departments.filter(
                Q(title__contains=query) | Q(code__contains=query)
            )
        return Response(DepartmentSerializer(departments, many=True).data)

    def create(self, request: Request):
        """Accept valid from to create a new department into the system

        Args:
            request (Request): _description_

        Returns:
            _type_: _description_
        """

        if not userIsAdmin(request):
            raise PermissionDenied("Only admin user can create new department")

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
                    **DepartmentSerializer(department).data,  # type: ignore
                    "staffs": PlainStaffSerializer(staffs, many=True).data,
                    "courses": PlainCourseSerializer(courses, many=True).data,
                }
            )
        except Department.DoesNotExist:
            return Response(
                {"Details": "Department not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=False,
        methods=("POST", "DELETE"),
        permission_classes=(IsAuthenticated, IsAdmin),
    )
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

    @action(
        methods=("DELETE",), detail=False, permission_classes=(IsAuthenticated, IsAdmin)
    )
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
        if not userIsAdmin(request):
            raise PermissionDenied("Only admin user can delete a department")
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
    def courses(self, request: Request, pk=None):
        """Returns list of courses that belongs to the department with id of {pk}

        Args:
            request (Request): _description_
            pk (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        try:
            department = Department.objects.get(pk=pk)
            courses = Course.objects.filter(department=department)
            return Response(CourseSerializer(courses, many=True).data)
        except Department.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Department not found"},
            )

    @action(detail=True)
    def staffs(self, request: Request, pk=None):
        """Returns list of staffs that belong to th department with id of {pk}

        Args:
            request (Request): _description_
            pk (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        try:
            department = Department.objects.get(pk=pk)
            staffs = Staff.objects.filter(department=department)
            return Response(StaffSerializer(staffs, many=True).data)
        except Department.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"details": "Department not found"},
            )


class VenueViewSet(ViewSet):
    def list(self, request: Request):
        """Returns he list of venues in the system

        Args:
            request (Request): _description_

        Returns:
            _type_: _description_
        """
        venues = Venue.objects.all()
        query = request.query_params.get("q", None)
        if query:
            venues = venues.filter(Q(title__icontainx=query) | Q(code__icontains=query))

        return Response(VenueSerializer(venues, many=True).data)

    @action(methods=("GET", "POST", "DELETE"), detail=False)
    def categories(self, request: Request):
        """Handles listing, deleting and adding new venue category based on the method type
        post : for creating
        delete: for deleting
        get: for listing

        Args:
            request (Request): _description_

        Raises:
            PermissionDenied: _description_

        Returns:
            _type_: _description_
        """
        if not userIsAdmin(request) and request._request.method in ("DELETE", "POST"):
            raise PermissionDenied("This action is only available to admin users")
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

        if not userIsAdmin(request):
            raise PermissionDenied("Only admin user can create new venues")
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

    @action(
        methods=("DELETE",), detail=False, permission_classes=(IsAuthenticated, IsAdmin)
    )
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
        if not userIsAdmin(request):
            raise PermissionDenied("Only admin users can add new staff")
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

    def update(self, request: Request, pk: None):
        try:
            staff = Staff.objects.get(pk=pk)

            if not userIsAdmin(request):
                raise PermissionDenied("Only admin users can add new staff")
            form = UpdateStaffForm(request.data)  # type: ignore
            if not form.is_valid():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "details": "Invalid form",
                        "errors": form.errors,
                        "fields": form.errors.keys(),
                    },
                )

            _staff = form.cleaned_data
            staff.name = _staff["name"]
            staff.can_invigilate = _staff["can_invigilate"]
            staff.can_supervise = _staff["can_supervise"]
            staff.staff_id = _staff["staff_id"]
            staff.department = _staff["department"]

            if (
                Staff.objects.filter(staff_id=_staff["staff_id"])
                .exclude(pk=staff.pk)
                .count()
                > 0
            ):
                return Response(
                    status=status.HTTP_409_CONFLICT,
                    data={"details": "Staff Id used by another staff"},
                )

            staff.save()
            return Response(StaffSerializer(staff).data)
        except Staff.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"details": "No staff found"}
            )

    def retrieve(self, request: Request, pk=None):
        try:
            staff = Staff.objects.get(pk=pk)
            return Response(StaffSerializer(staff).data)
        except Staff.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"details": "Staff not found"}
            )

    @action(
        detail=False,
        methods=("POST", "DELETE"),
        permission_classes=(IsAuthenticated, IsAdmin),
    )
    def multiple(self, request: Request):
        request_method = request._request.method

        staffs_pks: list[int] = request.data  # type: ignore

        if request_method == "POST":
            staffs = Staff.objects.filter(Q(pk__in=staffs_pks))
            return Response(StaffSerializer(staffs, many=True).data)
        elif request_method == "DELETE":
            staffs = Staff.objects.filter(Q(pk__in=staffs_pks))
            staffs.delete()
            return Response(StaffSerializer(staffs, many=True).data)
        else:
            raise MethodNotAllowed(method=request_method)

    def delete(self, request: Request, pk=None):
        if not userIsAdmin(request):
            raise PermissionDenied("Only admin user can delete a staff")
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
