from rest_framework import serializers
from .models import Athlete

class AthleteSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(read_only=True)

    def validate_user(self, value):
        if not value:
            return value
        linked_athlete = getattr(value, "athlete", None)
        if linked_athlete and (not self.instance or linked_athlete.id != self.instance.id):
            raise serializers.ValidationError("Este usuário já está vinculado a outro atleta.")
        return value

    class Meta:
        model = Athlete
        fields = "__all__"


class AthleteMeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Athlete
        fields = (
            "name",
            "jersey_number",
            "photo",
            "birth_date",
            "birth_city",
            "height_m",
            "weight_kg",
            "career_notes",
        )