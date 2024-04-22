from django.shortcuts import render
from django.http.request import HttpRequest

from .forms import ImporterForm
import json

from core.models import Course, Department

# Create your views here.


def importer(request: HttpRequest):
    if request.method == "GET":
        return render(
            request=request,
            template_name="debug/importer.html",
            context={"form": ImporterForm()},
        )

    else:
        form = ImporterForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(
                request=request,
                template_name="debug/importer.html",
                context={
                    "form": form,
                    "error": "Invalid form",
                },
            )

        res = handle_uploaded_file(request.FILES["file"])
        return render(request=request, template_name="debug/details.html", context=res)

    return render(request=request, template_name="debug/importer.html")


def handle_uploaded_file(file):
    data: dict = json.loads(file.read())

    departments: set[str] = set(data.keys())

    imported_courses = []

    for department_code in departments:
        department_courses: dict = data[department_code]

        department = Department.objects.filter(code__iexact=department_code.replace("cmp","cs")).first()

        if not department:
            print(f"{department_code} Not found")
            continue

        levels = set(department_courses.keys())

        for level in levels:
            level_courses = department_courses[level]

            for temp_course in level_courses:
                title = temp_course[0]
                code = temp_course[1]
                unit = temp_course[2]
                count = temp_course[3]

                try:
                    course = Course.objects.get(code=code)
                    if course.departments.filter(code=department.code).count() == 0:
                        course.departments.add(department)
                        course.student_count = course.student_count + count
                        course.save()
                        imported_courses.append(course)

                except Course.DoesNotExist:
                    course = Course(title=title, code=code)
                    course.department = department
                    course.student_count = count
                    course.level = int(level)
                    course.semester = 1
                    course.save()
                    course.departments.set([department])
                    imported_courses.append(course)

    print(f"{len(imported_courses)} Courses imported")
    return {
        "departments": list(map(lambda e: e.upper(), departments)),
        "courses": imported_courses,
    }
