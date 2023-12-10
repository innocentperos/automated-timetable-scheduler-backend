from core.models import Course


def flatten_course_department(courses: list[Course]):
    departments = set()
    for course in courses:
        departments.add(f"{course.department.code}-{course.level}")

    return departments
