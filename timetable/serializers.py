from rest_framework import serializers

from timetable.models import Timetable

class TimetableSerializer(serializers.ModelSerializer):

    pk = serializers.IntegerField()
    class Meta:
        model = Timetable 
        fields = "__all__"