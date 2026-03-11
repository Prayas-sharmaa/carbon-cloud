from django.db import models
from django.contrib.auth.models import User


class CarbonEntry(models.Model):
    ACTIVITY_CHOICES = [
        ("transport", "Transport"),
        ("electricity", "Electricity"),
        ("food", "Food"),
        ("shopping", "Shopping"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carbon_entries")
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    emission_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="CO2 in kg")
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name_plural = "Carbon Entries"

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.emission_amount}kg CO2"