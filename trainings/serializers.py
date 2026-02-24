from rest_framework import serializers
from .models import TrainingSession, Attendance, DrillCatalog, TrainingDrill, DrillScore

class DrillCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrillCatalog
        fields = "__all__"

class AttendanceSerializer(serializers.ModelSerializer):
    athlete_name = serializers.CharField(source="athlete.name", read_only=True)

    class Meta:
        model = Attendance
        fields = "__all__"

class DrillScoreSerializer(serializers.ModelSerializer):
    athlete_name = serializers.CharField(source="athlete.name", read_only=True)

    class Meta:
        model = DrillScore
        fields = "__all__"

    def validate_score(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError("A nota deve estar entre 0 e 10.")
        return value

class TrainingDrillSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    scores = DrillScoreSerializer(many=True, read_only=True)

    class Meta:
        model = TrainingDrill
        fields = "__all__"

class TrainingSessionSerializer(serializers.ModelSerializer):
    drills = TrainingDrillSerializer(many=True, read_only=True)
    attendances = AttendanceSerializer(many=True, read_only=True)

    class Meta:
        model = TrainingSession
        fields = "__all__"