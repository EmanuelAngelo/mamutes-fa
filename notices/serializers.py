from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Notice, NoticeComment, PushSubscription

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class NoticeCommentSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = NoticeComment
        fields = ("id", "user", "text", "created_at")


class NoticeSerializer(serializers.ModelSerializer):
    created_by = UserPublicSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    liked_by_me = serializers.BooleanField(read_only=True)
    recent_comments = NoticeCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Notice
        fields = (
            "id",
            "title",
            "body",
            "created_by",
            "created_at",
            "updated_at",
            "likes_count",
            "comments_count",
            "liked_by_me",
            "recent_comments",
        )


class NoticeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ("title", "body")

    def validate_body(self, value: str) -> str:
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("Informe o texto do aviso.")
        return v


class NoticeCommentCreateSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=800, allow_blank=False, trim_whitespace=True)

    def validate_text(self, value: str) -> str:
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("Informe um comentário.")
        return v


class PushSubscriptionUpsertSerializer(serializers.Serializer):
    endpoint = serializers.CharField()
    keys = serializers.DictField(child=serializers.CharField(), allow_empty=False)
    user_agent = serializers.CharField(required=False, allow_blank=True, max_length=255)

    def validate(self, attrs):
        keys = attrs.get("keys") or {}
        p256dh = keys.get("p256dh")
        auth = keys.get("auth")
        if not p256dh or not auth:
            raise serializers.ValidationError({"keys": "Informe keys.p256dh e keys.auth."})
        return attrs


class PushSubscriptionUnsubscribeSerializer(serializers.Serializer):
    endpoint = serializers.CharField()


class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ("id", "endpoint", "created_at", "updated_at")
