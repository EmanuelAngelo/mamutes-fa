from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import SavingsGoal, Transaction

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class SavingsGoalSerializer(serializers.ModelSerializer):
    created_by = UserPublicSerializer(read_only=True)
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = SavingsGoal
        fields = (
            "id",
            "name",
            "target_amount",
            "current_amount",
            "category",
            "deadline",
            "notes",
            "status",
            "user",
            "created_by",
            "created_at",
            "updated_at",
        )


class SavingsGoalCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsGoal
        fields = (
            "name",
            "target_amount",
            "category",
            "deadline",
            "notes",
            "status",
        )

    def validate_name(self, value: str) -> str:
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("Informe um nome.")
        return v

    def validate_target_amount(self, value):
        if value is None:
            raise serializers.ValidationError("Informe o valor alvo.")
        if Decimal(value) <= 0:
            raise serializers.ValidationError("O valor alvo deve ser maior que zero.")
        return value

    def validate_notes(self, value: str) -> str:
        return (value or "").strip()




class TransactionSerializer(serializers.ModelSerializer):
    created_by = UserPublicSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "goal",
            "amount",
            "type",
            "note",
            "created_by",
            "created_at",
        )
        read_only_fields = ("goal", "created_by", "created_at")


class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("amount", "type", "note")

    def validate_amount(self, value):
        if value is None:
            raise serializers.ValidationError("Informe um valor.")
        if Decimal(value) <= 0:
            raise serializers.ValidationError("O valor deve ser maior que zero.")
        return value

    def validate_note(self, value: str) -> str:
        return (value or "").strip()
