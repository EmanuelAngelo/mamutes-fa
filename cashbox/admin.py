from django.contrib import admin

from .models import SavingsGoal, Transaction


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "created_by",
        "category",
        "status",
        "current_amount",
        "target_amount",
        "created_at",
    )
    list_select_related = ("user", "created_by")
    search_fields = ("name", "notes", "user__username", "created_by__username")
    list_filter = ("category", "status")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "goal", "type", "amount", "created_by", "created_at")
    list_select_related = ("goal", "created_by")
    search_fields = ("goal__name", "note", "created_by__username")
    list_filter = ("type", "created_at")
