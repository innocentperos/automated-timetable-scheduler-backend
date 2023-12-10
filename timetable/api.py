from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action

from timetable.models import Timetable
from timetable.serializers import TimetableSerializer


class TimetableViewSet(ViewSet):
    def list(self, request: Request):
        tables = Timetable.objects.all()

        return Response(TimetableSerializer(tables, many=True).data)
