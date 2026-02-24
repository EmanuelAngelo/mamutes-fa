from django.contrib import admin
from .models import Athlete

@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ("name", "jersey_number", "current_position", "is_active")
    search_fields = ("name",)
    list_filter = ("current_position", "is_active")