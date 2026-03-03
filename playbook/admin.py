from django.contrib import admin

from .models import Play


@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "play_type", "formation", "created_at")
    list_filter = ("category",)
    search_fields = ("name", "description")
    ordering = ("-created_at",)
