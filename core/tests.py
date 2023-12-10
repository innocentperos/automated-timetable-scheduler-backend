import random

from django.test import TestCase
from django.db import IntegrityError

from core.models import Department, Course


# Create your tests here.
class TestDepartment(TestCase):

    def test_adding_department(self):
        department = Department(title="Computer Science", code="CS", )
        self.assertTrue(Department.objects.count() == 0,
                        "Starting department test with empty departments")
        department.save()
        self.assertTrue(Department.objects.count() == 1, "Added on department")

        with self.assertRaises(IntegrityError, msg="Another Department with the same code exist"):
            department = Department(title="Computer Science", code="CS", )
            department.save()


class TestCourseModel(TestCase):

    def test_adding_course(self):
        department = Department(title="Computer Science", code="CS", )
        department.save()

        course = Course(title="Course A", code="A", student_count=100, department=department, )
        course.save()

        self.assertTrue(Course.objects.count() == 1, msg="added on Course")

    def test_adding_multiple_courses(self):

        for d in range(5):
            department = Department(title=f"Department {d}", code=f"D-{d}", )
            department.save()

        else:
            departments = list(Department.objects.all())
            self.assertTrue(len(departments) == 5, "Added 5 departments")

        for i in range(10):
            course = Course(title=f"Course {i}", code=f"C-{i}", student_count=random.randint(10, 200),
                            department=random.choice(departments))
            course.save()

        else:
            self.assertTrue(Course.objects.count() == 10, "Added 10 courses")
