from rest_framework import serializers

from .models import Play


class PlaySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    clear_image = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = Play
        fields = (
            "id",
            "title",
            "description",
            "category",
            "image",
            "image_url",
            "clear_image",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {
            "image": {"required": False, "allow_null": True},
            "category": {"required": False, "allow_null": True},
            "description": {"required": False, "allow_null": True},
        }

    def get_image_url(self, obj: Play):
        if not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url

    def update(self, instance: Play, validated_data):
        clear_image = bool(validated_data.pop("clear_image", False))
        if clear_image and instance.image:
            instance.image.delete(save=False)
            instance.image = None

        return super().update(instance, validated_data)

    def create(self, validated_data):
        # Non-model write-only helper.
        validated_data.pop("clear_image", None)
        return super().create(validated_data)
