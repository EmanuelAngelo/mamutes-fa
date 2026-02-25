from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("role",)

class MeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="profile.role", read_only=True)
    athlete_id = serializers.IntegerField(source="athlete.id", read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role", "athlete_id")