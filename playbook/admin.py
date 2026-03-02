from django.contrib import admin

from .models import Play


@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "created_at")
    list_filter = ("category",)
    search_fields = ("title", "description")
    ordering = ("-created_at",)
