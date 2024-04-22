from django import forms

class ImporterForm(forms.Form):
    file = forms.FileField()