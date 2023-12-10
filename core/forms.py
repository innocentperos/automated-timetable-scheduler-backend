from django import forms

from core.models import Department, Course, Venue


class AddDepartmentForm(forms.ModelForm):
    title = forms.CharField(label="Department Title")

    class Meta:
        model = Department
        fields = ("title", "code")


class AddCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ("title", "code", "department", "level", "semester", "student_count", "departments")


class AddVenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ("title", "code", "category", "capacity")

class AddVenueCategoryForm(forms.Form):
    title = forms.CharField()