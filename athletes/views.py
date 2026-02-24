from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdminOrCoach
from .models import Athlete
from .serializers import AthleteSerializer


class AthleteViewSet(ModelViewSet):
    queryset = Athlete.objects.all().order_by("name")
    serializer_class = AthleteSerializer
    filterset_fields = ("is_active", "current_position", "desired_position")
    search_fields = ("name", "birth_city")
    ordering_fields = ("name", "jersey_number", "created_at")

    def get_permissions(self):
        # CRUD geral é só Admin/Coach
        if self.action in ("list", "create", "update", "partial_update", "destroy", "retrieve"):
            return [IsAuthenticated(), IsAdminOrCoach()]
        return [IsAuthenticated()]

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Retorna a ficha do atleta vinculado ao usuário logado.
        Requer que Athlete.user esteja preenchido.
        """
        athlete = getattr(request.user, "athlete", None)
        if not athlete:
            return Response(
                {"detail": "Este usuário não está vinculado a nenhum atleta."},
                status=404,
            )
        return Response(AthleteSerializer(athlete).data)