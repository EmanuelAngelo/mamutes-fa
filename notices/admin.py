from django.contrib import admin

from .models import Notice, NoticeComment, NoticeLike


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_by", "created_at")
    search_fields = ("title", "body", "created_by__username")
    list_select_related = ("created_by",)


@admin.register(NoticeComment)
class NoticeCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "notice", "user", "created_at")
    search_fields = ("text", "user__username")
    list_select_related = ("notice", "user")


@admin.register(NoticeLike)
class NoticeLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "notice", "user", "created_at")
    list_select_related = ("notice", "user")
