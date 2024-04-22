from django import forms

from core.models import Department, Course, Staff, Venue


class AddDepartmentForm(forms.ModelForm):
    title = forms.CharField(label="Department Title")

    class Meta:
        model = Department
        fields = ("title", "code")


class AddCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            "title",
            "code",
            "department",
            "level",
            "semester",
            "student_count",
            "departments",
        )
        
class UpdateCourseForm(forms.ModelForm):
    code = forms.CharField(required=True)
    class Meta:
        model = Course
        fields = (
            "title",
            "id",
            "department",
            "level",
            "semester",
            "student_count",
            "departments",
        )



class AddVenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ("title", "code", "category", "capacity")


class AddVenueCategoryForm(forms.Form):
    title = forms.CharField()


class AddStaffForm(forms.ModelForm):
    email = forms.CharField(required=False)

    class Meta:
        model = Staff
        fields = (
            "name",
            "staff_id",
            "department",
            "can_supervise",
            "can_invigilate",
        )


class UpdateStaffForm(forms.Form):
    name = forms.CharField()
    staff_id = forms.CharField()
    department = forms.ModelChoiceField(Department.objects)
    can_supervise = forms.BooleanField()
    can_invigilate = forms.BooleanField()
    