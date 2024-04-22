from django import forms
from account.models import USER_STAFF, USER_STUDENT
from core.models import Department


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=400, required=True)
    password = forms.CharField(required=True)


class RegisterForm(forms.Form):
    STUDENT_USER_TYPE = USER_STUDENT
    STAFF_USER_TYPE = USER_STAFF
    first_name = forms.CharField()
    last_name = forms.CharField()

    email = forms.EmailField(max_length=400, required=True)
    password = forms.CharField(required=True)
    user_type = forms.ChoiceField(
        choices=((STUDENT_USER_TYPE, "student"), (STAFF_USER_TYPE, "staff"))
    )
    department = forms.ModelChoiceField(
        Department.objects,
    )
    level = forms.ChoiceField(
        choices=(
            (100, "100L"),
            (200, "200L"),
            (300, "300L"),
            (400, "400L"),
            (500, "500L"),
        ),
        required=False,
    )
