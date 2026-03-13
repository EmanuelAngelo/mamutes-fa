from django.conf import settings
from django.db import migrations, models
from django.db.models import F


def backfill_goal_user(apps, schema_editor):
    SavingsGoal = apps.get_model("cashbox", "SavingsGoal")
    db_alias = schema_editor.connection.alias
    (
        SavingsGoal.objects.using(db_alias)
        .filter(user__isnull=True, created_by__isnull=False)
        .update(user=F("created_by"))
    )


class Migration(migrations.Migration):
    dependencies = [
        ("cashbox", "0003_alter_transaction_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="savingsgoal",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name="savings_goals",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(backfill_goal_user, migrations.RunPython.noop),
    ]
