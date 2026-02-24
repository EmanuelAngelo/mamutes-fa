from rest_framework import serializers
from .models import TestType, AssessmentEvent, AssessmentResult

class TestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestType
        fields = "__all__"

class AssessmentEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentEvent
        fields = "__all__"

class AssessmentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentResult
        fields = "__all__"