from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db.models import Avg, Case, ExpressionWrapper, F, FloatField, Sum, Value, When
from django.db.models.functions import Coalesce

from accounts.permissions import IsAdminOrCoach
from .models import Athlete
from .serializers import AthleteSerializer, AthleteMeUpdateSerializer


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

    def _with_rating(self, qs):
        numerator_expr = ExpressionWrapper(
            F("drill_scores__score") * F("drill_scores__training_drill__weight"),
            output_field=FloatField(),
        )
        weight_expr = ExpressionWrapper(
            F("drill_scores__training_drill__weight"),
            output_field=FloatField(),
        )

        qs = qs.annotate(
            rating_points=Coalesce(Sum(numerator_expr), Value(0.0)),
            rating_weight=Coalesce(Sum(weight_expr), Value(0.0)),
        ).annotate(
            rating=Case(
                When(
                    rating_weight__gt=0,
                    then=ExpressionWrapper(
                        F("rating_points") / F("rating_weight"),
                        output_field=FloatField(),
                    ),
                ),
                default=Value(0.0),
                output_field=FloatField(),
            )
        )
        return qs

    def get_queryset(self):
        qs = Athlete.objects.all()
        qs = self._with_rating(qs)
        return qs.order_by("name")

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated, IsAdminOrCoach])
    def stats(self, request):
        qs = self.filter_queryset(self.get_queryset())
        total = qs.count()
        avg_rating = qs.aggregate(v=Avg("rating"))["v"] or 0.0
        top = qs.order_by("-rating", "name").first()
        return Response({
            "total": total,
            "avg_rating": round(float(avg_rating), 2),
            "top_performer": (
                {
                    "id": top.id,
                    "name": top.name,
                    "rating": round(float(getattr(top, "rating", 0.0) or 0.0), 2),
                }
                if top
                else None
            ),
        })

    @action(detail=False, methods=["get", "patch"], permission_classes=[IsAuthenticated])
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

        if request.method.upper() == "PATCH":
            serializer = AthleteMeUpdateSerializer(
                athlete,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        athlete_qs = self._with_rating(Athlete.objects.filter(id=athlete.id))
        athlete_with_rating = athlete_qs.first() or athlete
        return Response(AthleteSerializer(athlete_with_rating).data)