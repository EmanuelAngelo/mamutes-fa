from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminOrCoach
from .models import TestType, AssessmentEvent, AssessmentResult
from .serializers import TestTypeSerializer, AssessmentEventSerializer, AssessmentResultSerializer

class TestTypeViewSet(ModelViewSet):
    queryset = TestType.objects.all().order_by("name")
    serializer_class = TestTypeSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdminOrCoach()]
        return [IsAuthenticated()]

class AssessmentEventViewSet(ModelViewSet):
    queryset = AssessmentEvent.objects.all().order_by("-date")
    serializer_class = AssessmentEventSerializer
    filterset_fields = ("season_year", "date")
    ordering_fields = ("date", "season_year")

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdminOrCoach()]
        return [IsAuthenticated()]

class AssessmentResultViewSet(ModelViewSet):
    queryset = AssessmentResult.objects.all()
    serializer_class = AssessmentResultSerializer
    filterset_fields = ("athlete", "event", "test_type")

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdminOrCoach()]
        return [IsAuthenticated()]