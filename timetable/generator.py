from django.db import transaction
from django.db.models import Q, Count
from django.utils import log
from core.models import Department, Course, Venue, Staff
from typing import Iterable, TypeAlias, TypeVar, Callable, Any
import math
import random

from timetable.qeueing import Queue, each


class Slot:
    def __init__(self, index: int) -> None:
        self.index = index
        self.courses: set[Course] = set()
        self.departments: dict[str, set[int]] = {}
        pass

    def clear(self):
        self.courses: set[Course] = set()
        self.departments: dict[str, set[int]] = {}

    def has_level(self, level: int, department: Department):
        if department.code not in self.departments:
            return False

        levels = self.departments[department.code]
        return level in levels

    def slot_day(self, slot_per_day: int):
        return math.ceil(self.index / slot_per_day)

    def add_course(self, course: Course) -> bool:
        for department in course.departments.all():
            if self.has_level(course.level, department):
                return False

        self.courses.add(course)

        for department in course.departments.all():
            # Loop over each department of the course
            if department.code not in self.departments:
                self.departments[department.code] = set()

            self.departments[department.code].add(course.level)

        return True

    def remove_course(self, course_to_remove: Course):
        if course_to_remove not in self.courses:
            return True

        self.courses.remove(course_to_remove)
        self.departments.clear()

        for course in self.courses:
            # loop over the courses in the slot

            for department in course.departments.all():
                # Loop over each department of the course
                if department.code not in self.departments:
                    self.departments[department.code] = set([course.level])

                else:
                    self.departments[department.code].add(course.level)
        return True


class Generator:
    def __init__(
        self,
        courses: list[Course],
        slot_per_day: int,
        days_count: int,
    ) -> None:
        self.courses = courses
        self.slot_per_day = slot_per_day
        self.days_count = days_count

        self.ignored_courses: set[Course] = set()

        self.slots: list[Slot] = []

        for slot_index in range(days_count * slot_per_day):
            self.slots.append(Slot(slot_index + 1))

        pass

    def get_day_slots(self, day: int):
        return list(
            filter(lambda slot: slot.slot_day(self.slot_per_day) == day, self.slots)
        )

    def get_adjacent_slots(self, slot: Slot):
        return list(
            filter(
                lambda _slot: _slot.slot_day(self.slot_per_day)
                == slot.slot_day(self.slot_per_day)
                and _slot.index in [slot.index - 1, slot.index + 1],
                self.slots,
            )
        )

    def start(self):
        # Sort courses by department counts
        self.courses.sort(key=lambda course: course.departments.count(), reverse=True)
        each(lambda slot: slot.clear(), self.slots)

        for course in self.courses:
            random.shuffle(self.slots)
            slot_pool: Queue[Slot] = Queue(self.slots)

            while slot_pool.count() > 0:
                # Iterate over all the slot in the slot pool and try adding the course,
                # If it fails pop the next slot and try again, if slot pool is empty
                # Add the course to ignored courses
                print(f"Queue counting : {slot_pool.count()}")
                slot = slot_pool.pop()
                if slot.add_course(course):
                    break
            else:
                print("Ignored Course")
                self.ignored_courses.add(course)

    def get_slots_courses(self, slots: Iterable[Slot]):
        courses = set()
        each(lambda slot: courses.update(slot.courses), slots)
        return courses

    def get_courses_venues(self, courses: Iterable[Course]):
        venues: set[Venue] = set()
        for course in courses:
            if course in self.course_assigned_venues:
                venues.update(self.course_assigned_venues[course])
        return venues

    def select_multiple_venue(self, venues: Iterable[Venue], capacity: int):
        _venues = Queue(list(venues))
        selected_venues = []
        current_capacity = 0
        while len(_venues) > 0:
            venue = _venues.pop()
            selected_venues.append(venue)
            current_capacity = current_capacity + venue.capacity
            if current_capacity > capacity:
                return selected_venues
        return None

    def assign_venues(self, venues: list[Venue]):
        self.course_assigned_venues: dict[Course, set[Venue]] = {}
        self.unassigned_venue_courses: set[Course] = set()

        _venues = set(venues)
        for slot in self.slots:
            adjacent_slots = self.get_adjacent_slots(slot)
            adjacent_slots_courses = self.get_slots_courses(adjacent_slots)
            exclude_venues = self.get_courses_venues(adjacent_slots_courses)

            _venue_pool = sorted(
                list(_venues - exclude_venues),
                key=lambda venue: venue.capacity,
                reverse=True,
            )

            courses = sorted(
                slot.courses, key=lambda course: course.student_count, reverse=True
            )

            for course in courses:
                # TODO This filtering here will not work
                # if all the venues capacity are morethan 130% of the course student count.
                _single_possible_venue_pool = list(
                    filter(
                        lambda venue: venue.capacity > course.student_count
                        # TODO 1.3 is the margin for accuracy for student spacing
                        and venue.capacity <= course.student_count * 1.3,
                        _venue_pool,
                    )
                )

                if len(_single_possible_venue_pool) > 0:
                    # There is sutable venue
                    selected_venue = random.choice(_single_possible_venue_pool)
                    self.course_assigned_venues[course] = set([selected_venue])
                    _venue_pool.remove(
                        selected_venue
                    )  # Remove selected venue from the venue pool

                else:
                    # multiple venues is required
                    selected_venues = self.select_multiple_venue(
                        _venue_pool, course.student_count
                    )

                    if selected_venues != None:
                        self.course_assigned_venues[course] = set(selected_venues)
                        # remove the selected venues from the pool
                        each(lambda venue: _venue_pool.remove(venue), selected_venues)
                    else:
                        # No venues to contain this course
                        self.unassigned_venue_courses.add(course)


