class CarbonEntryForm(forms.ModelForm):
    class Meta:
        model = CarbonEntry
        fields = ["activity_type", "emission_amount", "description", "date"]
        widgets = {
            "activity_type": forms.Select(attrs={"class": "form-input", "required": True}),
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
            # Remove "date" widget here; we'll add it in __init__
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the date widget with the current max date dynamically
        self.fields["date"].widget = forms.DateInput(
            attrs={
                "class": "form-input",
                "type": "date",
                "required": True,
                "max": timezone.now().date().isoformat(),
            }
        )

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