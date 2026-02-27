from django.contrib import admin

from .models import Play


@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "created_at")
    search_fields = ("title", "description")
    list_filter = ("category",)
