from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CarbonEntry


class CarbonEntryForm(forms.ModelForm):
    class Meta:
        model = CarbonEntry
        fields = ["activity_type", "emission_amount", "description", "date"]
        widgets = {
            "activity_type": forms.Select(attrs={"class": "form-input"}),
            "emission_amount": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "placeholder": "e.g. 5.2"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "What did you do?"}),
            "date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-input"}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-input"}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-input"}))

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"] = "form-input"
        self.fields["password1"].widget.attrs["class"] = "form-input"
        self.fields["password2"].widget.attrs["class"] = "form-input"