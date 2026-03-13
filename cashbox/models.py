from django.conf import settings
from django.db import models


class SavingsGoal(models.Model):
    class Category(models.TextChoices):
        TRAVEL = "viagem", "Viagem"
        TECHNOLOGY = "tecnologia", "Tecnologia"
        HOME = "casa", "Casa"
        CAR = "carro", "Carro"
        EDUCATION = "educacao", "Educação"
        HEALTH = "saude", "Saúde"
        EMERGENCY = "emergencia", "Emergência"
        OTHER = "outro", "Outro"

    class Status(models.TextChoices):
        ACTIVE = "ativa", "Ativa"
        COMPLETED = "concluida", "Concluída"
        PAUSED = "pausada", "Pausada"

    name = models.CharField(max_length=120)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    category = models.CharField(max_length=20, choices=Category.choices)
    deadline = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)

    # Owner of the goal (player/user who will see it).
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="savings_goals",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="savings_goals_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.name


class Transaction(models.Model):
    class Type(models.TextChoices):
        DEPOSIT = "deposito", "Depósito"
        WITHDRAW = "retirada", "Retirada"

    goal = models.ForeignKey(SavingsGoal, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=Type.choices)
    note = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="savings_transactions_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-id")

    def __str__(self) -> str:
        return f"{self.goal_id} {self.type} {self.amount}"
