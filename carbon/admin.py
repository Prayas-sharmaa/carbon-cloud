from django.contrib import admin
from .models import CarbonEntry


@admin.register(CarbonEntry)
class CarbonEntryAdmin(admin.ModelAdmin):
    list_display = ["user", "activity_type", "emission_amount", "date", "created_at"]
    list_filter = ["activity_type", "date"]
    search_fields = ["user__username", "description"]