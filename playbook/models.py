from django.conf import settings
from django.db import models


class Play(models.Model):
    class Category(models.TextChoices):
        ATAQUE = "ATAQUE", "Ataque"
        DEFESA = "DEFESA", "Defesa"
        # BOLA_PARADA = "BOLA_PARADA", "Bola Parada"
        # TRANSICAO = "TRANSICAO", "Transição"
        # POSSE = "POSSE", "Posse"

    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, blank=True)
    image = models.ImageField(upload_to="playbook/plays/", blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="playbook_plays",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return self.title
