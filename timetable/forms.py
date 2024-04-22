from django import forms
from core.models import Course

from timetable.models import ComplainMessage, SlotCourse, Timetable, Complain


class AddTimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ("title", "semester", "session")


class TimetableConfigurationForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = (
            "slot_per_day",
            "start_date",
            "end_date",
            "excluded_days",
            "excluded_week_days",
        )


class UpdateSlotCourse(forms.Form):
    venues = forms.Field(
        widget=forms.SelectMultiple,
        required=False,
    )
    invigilators = forms.Field(widget=forms.SelectMultiple, required=False)
    supervisor = forms.IntegerField(min_value=1)


class AddSlotCourseForm(forms.ModelForm):
    class Meta:
        model = SlotCourse
        fields = ("supervisor", "course", "slot")


class NewComplainForm(forms.ModelForm):
    message = forms.CharField()
    # related_slot_course = forms.IntegerField(min_value=1, required=False)
    # complain_type = forms.ChoiceField(
    #     choices=(
    #         (Complain.LEVEL_CONFLICT, "Level issue"),
    #         (Complain.OTHER_CONFLICT, "Other issue"),
    #     )
    # )
    # slot_course = forms.IntegerField(min_value=1)
    related_slot_course = forms.ModelChoiceField(SlotCourse.objects, required=False)
    related_course = forms.ModelChoiceField(Course.objects, required=False)
    

    class Meta:
        model = Complain
        fields = ("slot_course", "complain_type", "related_slot_course", "related_course")

class NewComplainMessageForm(forms.ModelForm):
    
    class Meta:
        model = ComplainMessage
        fields = ("message",)