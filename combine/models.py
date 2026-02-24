from django.db import models
from athletes.models import Athlete

class TestType(models.Model):
    code = models.CharField(max_length=30, unique=True)  # "40Y", "VJ", etc
    name = models.CharField(max_length=120)
    unit = models.CharField(max_length=20, null=True, blank=True)
    lower_is_better = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class AssessmentEvent(models.Model):
    name = models.CharField(max_length=120)  # "1º Trimestre 2026", "Combine Final 2026"
    season_year = models.PositiveIntegerField()
    date = models.DateField()

    def __str__(self):
        return self.name

class AssessmentResult(models.Model):
    event = models.ForeignKey(AssessmentEvent, on_delete=models.CASCADE, related_name="results")
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name="assessment_results")
    test_type = models.ForeignKey(TestType, on_delete=models.CASCADE, related_name="results")
    value = models.DecimalField(max_digits=8, decimal_places=2)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("event", "athlete", "test_type")