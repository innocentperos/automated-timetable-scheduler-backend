from rest_framework import serializers

from core.models import Course, Department, Staff, Venue, VenueCategory


class DepartmentSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField()
    course_count = serializers.IntegerField()
    staff_count = serializers.IntegerField()

    class Meta:
        model = Department
        fields = "__all__"


class PlainCourseSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    class Meta:
        model = Course
        fields = (
            "title",
            "code",
            "student_count",
            "department",
            "departments",
            "pk",
            "level",
            "level",
            "semester",
        )


class CourseSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    departments = DepartmentSerializer(many=True)

    class Meta:
        model = Course
        fields = (
            "title",
            "code",
            "student_count",
            "department",
            "departments",
            "pk",
            "level",
            "level",
            "semester",
        )


class VenueCategorySerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField()
    venue_count = serializers.IntegerField()

    class Meta:
        model = VenueCategory
        fields = "__all__"


class VenueSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField()
    category = VenueCategorySerializer()

    class Meta:
        model = Venue
        fields = "__all__"
        
class PlainVenueSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField()

    class Meta:
        model = Venue
        fields = "__all__"


class PlainStaffSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField()

    class Meta:
        model = Staff
        fields = "__all__"


class StaffSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField()
    department = DepartmentSerializer()

    class Meta:
        model = Staff
        fields = "__all__"
