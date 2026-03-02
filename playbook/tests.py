from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Profile
from playbook.models import Play


class PlaybookPermissionsTests(APITestCase):
    def setUp(self):
        self.player_user = User.objects.create_user(username="player", password="pass")
        self.player_user.profile.role = Profile.Role.PLAYER
        self.player_user.profile.save(update_fields=["role"])

        self.coach_user = User.objects.create_user(username="coach", password="pass")
        self.coach_user.profile.role = Profile.Role.COACH
        self.coach_user.profile.save(update_fields=["role"])

        self.play = Play.objects.create(title="Play 1", description="Desc", category="Ataque")

        self.list_url = reverse("playbook-plays-list")
        self.detail_url = reverse("playbook-plays-detail", args=[self.play.id])

    def test_player_can_list(self):
        self.client.force_authenticate(user=self.player_user)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_player_cannot_create(self):
        self.client.force_authenticate(user=self.player_user)
        resp = self.client.post(self.list_url, {"title": "New", "description": "x"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_player_cannot_delete(self):
        self.client.force_authenticate(user=self.player_user)
        resp = self.client.delete(self.detail_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_coach_can_create(self):
        self.client.force_authenticate(user=self.coach_user)
        resp = self.client.post(
            self.list_url,
            {"title": "New", "description": "x", "category": "Defesa"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
