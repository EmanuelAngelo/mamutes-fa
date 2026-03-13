from decimal import Decimal

from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminOrCoach
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import SavingsGoal, Transaction
from .serializers import (
    SavingsGoalCreateUpdateSerializer,
    SavingsGoalSerializer,
    TransactionCreateSerializer,
    TransactionSerializer,
)


class SavingsGoalViewSet(ModelViewSet):
    queryset = SavingsGoal.objects.all()
    serializer_class = SavingsGoalSerializer
    permission_classes = [IsAuthenticated]

    search_fields = ("name", "notes")
    ordering_fields = ("created_at", "updated_at", "name", "target_amount", "current_amount")

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAuthenticated(), IsAdminOrCoach()]
        return [IsAuthenticated()]

    def _is_admin_or_coach(self) -> bool:
        profile = getattr(self.request.user, "profile", None)
        return bool(profile and profile.role in ("ADMIN", "COACH"))

    def get_queryset(self):
        qs = SavingsGoal.objects.all().select_related("created_by", "user")

        # Everyone can see global goals (user=NULL). If in the future we create
        # personal goals, also include goals owned by the logged user.
        return qs.filter(Q(user__isnull=True) | Q(user=self.request.user))

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return SavingsGoalCreateUpdateSerializer
        return SavingsGoalSerializer

    def perform_create(self, serializer):
        # Coach/Admin creates global goals by default.
        serializer.save(user=None, created_by=self.request.user)

    @action(detail=True, methods=["get", "post"], url_path="transactions")
    def transactions(self, request, pk=None):
        goal = self.get_object()

        if request.method == "GET":
            qs = Transaction.objects.filter(goal=goal).select_related("created_by")
            return Response(TransactionSerializer(qs, many=True).data)

        if not self._is_admin_or_coach():
            raise PermissionDenied("Apenas coach/admin pode movimentar o cofrinho.")

        ser = TransactionCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        amount: Decimal = ser.validated_data["amount"]
        tx_type: str = ser.validated_data["type"]
        note: str = (ser.validated_data.get("note") or "").strip()

        current = goal.current_amount or Decimal("0.00")
        if tx_type == Transaction.Type.DEPOSIT:
            new_amount = current + amount
        else:
            new_amount = current - amount
            if new_amount < 0:
                new_amount = Decimal("0.00")

        tx = Transaction.objects.create(
            goal=goal,
            amount=amount,
            type=tx_type,
            note=note,
            created_by=request.user,
        )

        # Update goal amount and (optionally) status.
        goal.current_amount = new_amount
        if (
            goal.status != SavingsGoal.Status.COMPLETED
            and goal.target_amount
            and new_amount >= goal.target_amount
        ):
            goal.status = SavingsGoal.Status.COMPLETED
        goal.save(update_fields=["current_amount", "status", "updated_at"])

        return Response(
            {
                "transaction": TransactionSerializer(tx).data,
                "goal": SavingsGoalSerializer(goal).data,
            },
            status=status.HTTP_201_CREATED,
        )
