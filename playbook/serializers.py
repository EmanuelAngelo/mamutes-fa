from rest_framework import serializers

from .models import Play


class PlaySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    remove_image = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = Play
        fields = [
            "id",
            "title",
            "description",
            "category",
            "image",
            "image_url",
            "remove_image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "image_url"]

    def get_image_url(self, obj: Play):
        if not obj.image:
            return ""
        try:
            return obj.image.url
        except Exception:
            return ""

    def create(self, validated_data):
        validated_data.pop("remove_image", None)
        return super().create(validated_data)

    def update(self, instance: Play, validated_data):
        remove_image = bool(validated_data.pop("remove_image", False))
        if remove_image and instance.image:
            instance.image.delete(save=False)
            instance.image = None
        return super().update(instance, validated_data)
