from rest_framework import serializers

from core.models import Course, Department, Venue, VenueCategory


class DepartmentSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField()
    course_count = serializers.IntegerField()
    staff_count = serializers.IntegerField()

    class Meta:
        model = Department
        fields = "__all__"


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
