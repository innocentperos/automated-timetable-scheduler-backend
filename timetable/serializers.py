from rest_framework import serializers

"""
Serializers for the timetable app models.

TimetableSerializer and CreatedTimetableSerializer serialize the Timetable model.

SlotCourseSeriallizer serializes the SlotCourse model, including nested serialization of related Course, Staff, and Venue models. 

TimetableSlotSeriallizer serializes the TimetableSlot model, including nested serialization of related SlotCourse models.
"""
from core.serializers import (
    CourseSerializer,
    PlainCourseSerializer,
    PlainStaffSerializer,
    PlainVenueSerializer,
    StaffSerializer,
    VenueSerializer,
)

from timetable.models import (
    Complain,
    ComplainMessage,
    SlotCourse,
    Timetable,
    TimetableSlot,
)


class TimetableSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField()
    days_count = serializers.IntegerField()
    start_date = serializers.DateField(format="%Y-%m-%d")  # type: ignore
    end_date = serializers.DateField(format="%Y-%m-%d")  # type: ignore

    class Meta:
        model = Timetable
        fields = "__all__"


class CreatedTimetableSerializer(serializers.ModelSerializer):
    """
    Serializer for CreatedTimetable model instances.
    """

    pk = serializers.IntegerField()
    days_count = serializers.IntegerField()
    start_date = serializers.DateTimeField(format="%Y-%m-%d")  # type: ignore
    end_date = serializers.DateTimeField(format="%Y-%m-%d")  # type: ignore

    class Meta:
        model = Timetable
        fields = "__all__"


class ComplainMessageSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField()

    class Meta:
        model = ComplainMessage
        fields = "__all__"


class complainSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField()
    messages = ComplainMessageSerializer(many=True)

    class Meta:
        model = Complain
        fields = "__all__"


class SlotCourseSeriallizer(serializers.ModelSerializer):
    pk = serializers.IntegerField()
    course = CourseSerializer()
    supervisor = StaffSerializer()
    invigilators = StaffSerializer(many=True)
    venues = PlainVenueSerializer(many=True)
    complain_count = serializers.IntegerField()

    class Meta:
        model = SlotCourse
        fields = "__all__"


class MinimalTimetableSlotSeriallizer(serializers.ModelSerializer):
    """
    Minimal serializer for TimetableSlot model instances.
    """

    pk = serializers.IntegerField()
    course_count = serializers.IntegerField()

    class Meta:
        model = TimetableSlot
        fields = "__all__"


class TimetableSlotSeriallizer(serializers.ModelSerializer):
    pk = serializers.IntegerField()
    courses = SlotCourseSeriallizer(many=True)
    # The courses field serializes a list of SlotCourse model instances
    # using the SlotCourseSeriallizer serializer. The many=True argument
    # indicates this is a list of objects rather than a single object.

    class Meta:
        model = TimetableSlot
        fields = "__all__"
