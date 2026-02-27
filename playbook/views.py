from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import SAFE_METHODS
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsAdminOrCoach

from .models import Play
from .serializers import PlaySerializer


class PlayViewSet(ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title", "id"]
    filterset_fields = ["category"]

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return super().get_permissions()
        return [IsAdminOrCoach()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
