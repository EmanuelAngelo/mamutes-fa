from django.conf import settings
from django.db import models

class Athlete(models.Model):
    class Position(models.TextChoices):
        QUARTERBACK = "QB", "Quarterback"
        CENTER = "C", "Center"
        WIDE_RECEIVER = "WR", "Wide receiver"
        RUNNING_BACK = "RB", "Running back"
        DEFENSIVE_BACK = "DB", "Defensive back"
        BLITZ_RUSHER = "R", "Blitz/Rusher"
        SAFETY = "S", "Safety"
        CORNER_BACK = "CB", "Corne back"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="athlete",
        help_text="Vincule um usuário para permitir login do atleta."
    )

    name = models.CharField(max_length=120)
    jersey_number = models.PositiveIntegerField(null=True, blank=True)

    photo = models.ImageField(upload_to="athletes/photos/", null=True, blank=True)

    birth_date = models.DateField(null=True, blank=True)
    birth_city = models.CharField(max_length=120, null=True, blank=True)

    height_m = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    current_position = models.CharField(max_length=5, choices=Position.choices, null=True, blank=True)
    desired_position = models.CharField(max_length=5, choices=Position.choices, null=True, blank=True)

    career_notes = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name