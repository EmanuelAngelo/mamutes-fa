from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsAdminOrCoachOrReadOnly
from .models import Play
from .serializers import PlaySerializer


class PlayViewSet(ModelViewSet):
    queryset = Play.objects.all().order_by("-created_at")
    serializer_class = PlaySerializer
    permission_classes = [IsAdminOrCoachOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    search_fields = ("name", "description", "category")
    ordering_fields = ("created_at", "updated_at", "name")

    @action(detail=True, methods=["post"], url_path="clone")
    def clone(self, request, *args, **kwargs):
        src: Play = self.get_object()

        base_name = (src.name or "").strip() or "Jogada"
        suffix = " (cópia)"
        name = (base_name + suffix)[: Play._meta.get_field("name").max_length]

        clone = Play.objects.create(
            name=name,
            description=src.description,
            formation=src.formation,
            play_type=src.play_type,
            tags=list(src.tags or []),
            players=list(src.players or []),
            routes=list(src.routes or []),
            category=src.category,
            image=None,
        )

        serializer = self.get_serializer(clone)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
