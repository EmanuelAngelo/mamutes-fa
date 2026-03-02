from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsAdminOrCoachOrReadOnly
from .models import Play
from .serializers import PlaySerializer


class PlayViewSet(ModelViewSet):
    queryset = Play.objects.all().order_by("-created_at")
    serializer_class = PlaySerializer
    permission_classes = [IsAdminOrCoachOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    search_fields = ("title", "description", "category")
    ordering_fields = ("created_at", "updated_at", "title")
