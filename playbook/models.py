from django.db import models


class Play(models.Model):
    class Category(models.TextChoices):
        ATAQUE = "Ataque", "Ataque"
        DEFESA = "Defesa", "Defesa"

    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=30, choices=Category.choices, blank=True, null=True)

    image = models.ImageField(upload_to="playbook/plays/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title
