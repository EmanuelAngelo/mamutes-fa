from django.conf import settings
from django.db import models
from athletes.models import Athlete

class TrainingSession(models.Model):
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=160, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Treino {self.date}"

class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Presente"
        ABSENT = "ABSENT", "Ausente"
        JUSTIFIED = "JUSTIFIED", "Justificado"
        LATE = "LATE", "Atraso"

    training = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name="attendances")
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name="attendances")

    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PRESENT)
    checkin_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ("training", "athlete")

    def __str__(self):
        return f"{self.athlete.name} - {self.training.date} ({self.status})"

class DrillCatalog(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=60, null=True, blank=True)

    def __str__(self):
        return self.name

class TrainingDrill(models.Model):
    training = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name="drills")
    drill = models.ForeignKey(DrillCatalog, on_delete=models.SET_NULL, null=True, blank=True)
    name_override = models.CharField(max_length=120, null=True, blank=True)

    order = models.PositiveIntegerField(default=1)
    description = models.TextField(null=True, blank=True)

    max_score = models.PositiveIntegerField(default=10)
    weight = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)

    class Meta:
        ordering = ("order", "id")

    @property
    def name(self):
        return self.name_override or (self.drill.name if self.drill else "Drill")

    def __str__(self):
        return f"{self.training.date} - {self.name}"

class DrillScore(models.Model):
    training_drill = models.ForeignKey(TrainingDrill, on_delete=models.CASCADE, related_name="scores")
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name="drill_scores")

    score = models.DecimalField(max_digits=4, decimal_places=1)  # 0.0 a 10.0
    comment = models.TextField(null=True, blank=True)
    rated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("training_drill", "athlete")