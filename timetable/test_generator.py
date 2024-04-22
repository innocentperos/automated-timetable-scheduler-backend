import requests
import random

API = "http://localhost:8000/api"
department_request = requests.get(API+"/departments/")
DEPARTMENTS = department_request.json()
MAX_COURSE_PER_DEPARTMENT = 14
LEVELS = [100, 200, 300, 400]


class Course:
    def __init__(
        self,
        code: str,
        size: int,
        departments: list[str] = [],
        level: int = 100,
        index=-1,
    ) -> None:
        self.code = code
        self.size = size
        self.departments = departments
        self.level = level
        self.index = index

    def to_json(self):
        return {
            "code": self.code,
            "size": self.size,
            "level": self.level,
            "departments": self.departments,
        }

    def flatten(self):
        return (self.code, self.level, self.size, self.departments)

    def flatten_departments(self):
        # Returns the list of the departments and level in the format "{level}L-{department}"
        return map(lambda department: f"{self.level}L-{department}", self.departments)

    @staticmethod
    def create_course(level=100):
        department = random.choice(DEPARTMENTS)  # Chose the course department
        shared = (
            random.randrange(1, 50) == 7
        )  # Determine if the course is a mult department course
        departments = [department]

        if shared:
            departments = random.choice(SHARED_DEPARTMENT)
            while department not in departments:
                departments = random.choice(SHARED_DEPARTMENT)

            departments.remove(
                department
            )  # This two line makes sure that the course main department in the first department in it departments list
            departments.insert(0, department)

        suffix = random.randrange(level, level + 99)
        return Course(
            code=f"{department}-{suffix}",
            size=random.randrange(50, 250),
            departments=departments,
            level=level,
        )

    @staticmethod
    def create_batch_courses(count=50, level=100) -> tuple[list, dict[str, int]]:
        # Generate multiple course for a specific department

        courses: list[Course] = []
        courses_code = []

        departments_report: dict[str, int] = {}

        # calculate the departments that still have slot for more courses
        remaining_departments = (
            len(DEPARTMENTS)
            if len(departments_report.keys()) == 0
            else len(
                list(
                    filter(
                        lambda index: departments_report[index]
                        < MAX_COURSE_PER_DEPARTMENT,
                        departments_report,
                    )
                )
            )
        )

        while len(courses) < count and remaining_departments != 0:
            # Only run the loop , if the courses is not upto the required size
            # and their are remaining departments that have not reach their maximum courses per department

            course = Course.create_course(level)
            if course.code in courses_code:
                # Ignore as a course with thesame course code already exist
                continue

            departments = []
            for department in course.departments:
                # Removes any department that its courses is equal to te maximum course per department
                if department not in departments_report:
                    departments_report[department] = 0
                if departments_report[department] != MAX_COURSE_PER_DEPARTMENT:
                    departments.append(department)
                    departments_report[department] += 1

            if len(departments) > 0:
                # Only save the course if after filtering it departments, it departments is not empty
                course.departments = departments
                courses.append(course)
                courses_code.append(course.code)

            # Recalculate the departments that still have slot for more courses
            remaining_departments = len(
                list(
                    filter(
                        lambda index: departments_report[index]
                        < MAX_COURSE_PER_DEPARTMENT,
                        departments_report,
                    )
                )
            )

        return courses, departments_report

    @staticmethod
    def print_courses(courses: list):
        # Prints a list of courses grouped in level and department
        _courses: Iterable[Course] = courses

        for level in LEVELS:
            for department in DEPARTMENTS:
                department_courses = list(
                    filter(
                        lambda course: department in course.departments
                        and course.level == level,
                        _courses,
                    )
                )  # Filters the courses that are of the currently iterating level and contains the iterating department in it departments
                if len(department_courses) > 0:
                    # Only print the courses for the current level and department if the filtered courses is not empty
                    print(f"DEPARTMENT {department} {level}L")
                    forEach(
                        lambda course: print(f"\t{str(course)}"), department_courses
                    )

    @staticmethod
    def filter(
        courses: list,
        levels: list[int] | None = None,
        departments: list[str] | None = None,
    ):
        """
        Filters a list of courses whose level is inside [@params levels]
        and [@params departments] intersection with the course department is not empty
        """
        _courses: list[Course] = courses

        if levels:
            # apply level filtering it the level is provided
            _courses = list(filter(lambda course: course.level in levels, _courses))

        if departments:
            # apply department filtering if the departments is provided
            _courses = list(
                filter(
                    lambda course: len(
                        set(course.departments).intersection(set(departments))
                    )
                    > 0,
                    _courses,
                )
            )

        return _courses

    def __repr__(self) -> str:
        return f"{self.code} {self.departments}"
    
def generate_courses():
    _COURSES: list[Course] = []
    _LEVEL_STATS = {}

    for level in LEVELS:
        result = Course.create_batch_courses(
            MAX_COURSE_PER_DEPARTMENT * len(DEPARTMENTS), level=level
        )
        _COURSES = _COURSES + result[0]
        _LEVEL_STATS[level] = result[1]

    _COURSES.sort(key=lambda course: len(course.departments), reverse=True)
    print(f"{len(DEPARTMENTS)} Departments, {len(_COURSES)} Courses")
    return _COURSES, _LEVEL_STATS