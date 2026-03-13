from decimal import Decimal

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def forwards_map_goal_status_and_amounts(apps, schema_editor):
    SavingsGoal = apps.get_model("cashbox", "SavingsGoal")
    Transaction = apps.get_model("cashbox", "Transaction")

    # Map inactive -> pausada (field is_active still exists at this point)
    for goal in SavingsGoal.objects.all().only("id", "is_active", "status"):
        if hasattr(goal, "is_active") and goal.is_active is False:
            goal.status = "pausada"
            goal.save(update_fields=["status"])

    # Recalculate current_amount from existing transactions.
    for goal in SavingsGoal.objects.all().only("id"):
        total = Decimal("0.00")
        # Clear default ordering (historical model ordering may still reference removed fields).
        for tx in Transaction.objects.filter(goal_id=goal.id).order_by().only("amount", "type"):
            if tx.type == "deposito":
                total += tx.amount
            elif tx.type == "retirada":
                total -= tx.amount
        if total < 0:
            total = Decimal("0.00")
        SavingsGoal.objects.filter(id=goal.id).update(current_amount=total)

    # Mark completed where current_amount >= target_amount.
    for goal in SavingsGoal.objects.all().only("id", "current_amount", "target_amount", "status"):
        if goal.status != "concluida" and goal.target_amount and goal.current_amount >= goal.target_amount:
            goal.status = "concluida"
            goal.save(update_fields=["status"])


def forwards_map_transaction_kind_to_type(apps, schema_editor):
    Transaction = apps.get_model("cashbox", "Transaction")

    for tx in Transaction.objects.all().only("id", "kind"):
        if tx.kind == "IN":
            Transaction.objects.filter(id=tx.id).update(type="deposito")
        elif tx.kind == "OUT":
            Transaction.objects.filter(id=tx.id).update(type="retirada")
        else:
            Transaction.objects.filter(id=tx.id).update(type="deposito")


def backwards_noop(apps, schema_editor):
    # Non-reversible data migrations (best-effort).
    pass


def forwards_fill_null_target_amount(apps, schema_editor):
    SavingsGoal = apps.get_model("cashbox", "SavingsGoal")
    SavingsGoal.objects.filter(target_amount__isnull=True).update(target_amount=Decimal("0.00"))


class Migration(migrations.Migration):

    dependencies = [
        ("cashbox", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Fund",
            new_name="SavingsGoal",
        ),
        migrations.RenameModel(
            old_name="FundTransaction",
            new_name="Transaction",
        ),
        migrations.RenameField(
            model_name="savingsgoal",
            old_name="goal_amount",
            new_name="target_amount",
        ),
        migrations.RunPython(forwards_fill_null_target_amount, backwards_noop),
        migrations.RenameField(
            model_name="savingsgoal",
            old_name="description",
            new_name="notes",
        ),
        migrations.AddField(
            model_name="savingsgoal",
            name="current_amount",
            field=models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12),
        ),
        migrations.AddField(
            model_name="savingsgoal",
            name="category",
            field=models.CharField(
                choices=[
                    ("viagem", "Viagem"),
                    ("tecnologia", "Tecnologia"),
                    ("casa", "Casa"),
                    ("carro", "Carro"),
                    ("educacao", "Educação"),
                    ("saude", "Saúde"),
                    ("emergencia", "Emergência"),
                    ("outro", "Outro"),
                ],
                default="outro",
                max_length=20,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="savingsgoal",
            name="deadline",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="savingsgoal",
            name="status",
            field=models.CharField(
                choices=[("ativa", "Ativa"), ("concluida", "Concluída"), ("pausada", "Pausada")],
                default="ativa",
                max_length=12,
            ),
        ),
        migrations.AlterField(
            model_name="savingsgoal",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="savings_goals_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="savingsgoal",
            name="target_amount",
            field=models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12),
        ),
        migrations.RenameField(
            model_name="transaction",
            old_name="fund",
            new_name="goal",
        ),
        migrations.RenameField(
            model_name="transaction",
            old_name="description",
            new_name="note",
        ),
        # Add new `type` first (because existing `kind` is too short and has different choices)
        migrations.AddField(
            model_name="transaction",
            name="type",
            field=models.CharField(
                choices=[("deposito", "Depósito"), ("retirada", "Retirada")],
                default="deposito",
                max_length=10,
            ),
        ),
        migrations.RunPython(forwards_map_transaction_kind_to_type, backwards_noop),
        migrations.RemoveField(
            model_name="transaction",
            name="kind",
        ),
        migrations.RemoveField(
            model_name="transaction",
            name="occurred_at",
        ),
        migrations.RemoveField(
            model_name="transaction",
            name="category",
        ),
        migrations.AlterField(
            model_name="transaction",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="savings_transactions_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(forwards_map_goal_status_and_amounts, backwards_noop),
        migrations.RemoveField(
            model_name="savingsgoal",
            name="is_active",
        ),
    ]
