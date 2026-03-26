from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CarbonEntry
from django.core.exceptions import ValidationError
from django.utils import timezone


class CarbonEntryForm(forms.ModelForm):
    class Meta:
        model = CarbonEntry
        fields = ["activity_type", "emission_amount", "description", "date"]
        widgets = {
            "activity_type": forms.Select(
                attrs={"class": "form-input", "required": True}
            ),
            "emission_amount": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "step": "0.01",
                    "placeholder": "e.g. 5.2",
                    "min": "0.01",
                    "required": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "rows": 3,
                    "placeholder": "What did you do?",
                    "maxlength": "500",
                    "required": True,
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "class": "form-input",
                    "type": "date",
                    "required": True,
                    "max": timezone.now().date().isoformat(),  # Prevent future date 
                }
            ),
        }

    def clean_emission_amount(self):
        value = self.cleaned_data.get("emission_amount")
        if value is None or value <= 0:
            raise ValidationError("Emission amount must be greater than 0.")
        return value

    def clean_date(self):
        date = self.cleaned_data.get("date")
        if date > timezone.now().date():
            raise ValidationError("Date cannot be in the future.")
        return date


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"class": "form-input", "required": True})
    )
    first_name = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"class": "form-input", "required": True})
    )
    last_name = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"class": "form-input", "required": True})
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"] = "form-input"
        self.fields["username"].widget.attrs["required"] = True
        self.fields["password1"].widget.attrs["class"] = "form-input"
        self.fields["password1"].widget.attrs["required"] = True
        self.fields["password2"].widget.attrs["class"] = "form-input"
        self.fields["password2"].widget.attrs["required"] = True