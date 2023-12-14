from django import forms

from timetable.models import Timetable


class AddTimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ("title",)
