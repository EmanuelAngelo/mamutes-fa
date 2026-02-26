from datetime import date

from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient

from athletes.models import Athlete
from trainings.models import TrainingSession, Attendance, TrainingDrill, DrillScore


class CoachAnalyticsTests(APITestCase):
	def setUp(self):
		self.client = APIClient()

		self.coach = User.objects.create_user(username="coach", password="pw")
		# profile is auto-created by signal
		self.coach.profile.role = "COACH"
		self.coach.profile.save()
		self.client.force_authenticate(user=self.coach)

		self.a1 = Athlete.objects.create(name="A1", current_position="QB")
		self.a2 = Athlete.objects.create(name="A2", current_position="QB")
		self.a3 = Athlete.objects.create(name="A3", current_position="WR")
		self.a4 = Athlete.objects.create(name="A4", current_position="WR")

		self.t1 = TrainingSession.objects.create(date=date(2026, 1, 1), created_by=self.coach)
		for a in (self.a1, self.a2, self.a3, self.a4):
			Attendance.objects.create(training=self.t1, athlete=a, status="PRESENT")

		self.d1_t1 = TrainingDrill.objects.create(training=self.t1, name_override="D1", order=1, weight=2)
		self.d2_t1 = TrainingDrill.objects.create(training=self.t1, name_override="D2", order=2, weight=1)

		# Scores for analytics
		DrillScore.objects.create(training_drill=self.d1_t1, athlete=self.a1, score=9, rated_by=self.coach)
		DrillScore.objects.create(training_drill=self.d2_t1, athlete=self.a1, score=3, rated_by=self.coach)

		DrillScore.objects.create(training_drill=self.d1_t1, athlete=self.a2, score=8, rated_by=self.coach)
		DrillScore.objects.create(training_drill=self.d2_t1, athlete=self.a2, score=4, rated_by=self.coach)

		DrillScore.objects.create(training_drill=self.d1_t1, athlete=self.a3, score=6, rated_by=self.coach)
		DrillScore.objects.create(training_drill=self.d2_t1, athlete=self.a3, score=6, rated_by=self.coach)

		DrillScore.objects.create(training_drill=self.d1_t1, athlete=self.a4, score=4, rated_by=self.coach)
		DrillScore.objects.create(training_drill=self.d2_t1, athlete=self.a4, score=7, rated_by=self.coach)

	def test_training_analytics_endpoint(self):
		res = self.client.get(f"/api/trainings/{self.t1.id}/analytics/")
		self.assertEqual(res.status_code, 200)

		payload = res.json()
		self.assertEqual(payload["training"]["id"], self.t1.id)
		self.assertIn("distribution", payload)
		self.assertEqual(payload["distribution"]["total_scores"], 8)

		bins = {b["key"]: b["count"] for b in payload["distribution"]["bins"]}
		self.assertEqual(bins["0-4"], 3)
		self.assertEqual(bins["5-6"], 2)
		self.assertEqual(bins["7-8"], 2)
		self.assertEqual(bins["9-10"], 1)

		self.assertEqual(payload["hardest_drill"]["name"], "D2")
		self.assertEqual(payload["hardest_drill"]["avg_score"], 5.0)

		self.assertIsNotNone(payload["most_consistent_athlete"])
		self.assertEqual(payload["most_consistent_athlete"]["athlete_name"], "A3")
		self.assertEqual(payload["most_consistent_athlete"]["variance"], 0.0)

		by_pos = {p["position"]: p for p in payload["by_position"]}
		self.assertIn("QB", by_pos)
		self.assertIn("WR", by_pos)

	def test_evolution_endpoint_biggest_improvement_and_regression(self):
		t2 = TrainingSession.objects.create(date=date(2026, 1, 8), created_by=self.coach)
		for a in (self.a1, self.a2, self.a3, self.a4):
			Attendance.objects.create(training=t2, athlete=a, status="PRESENT")

		d1_t2 = TrainingDrill.objects.create(training=t2, name_override="D1", order=1, weight=2)
		d2_t2 = TrainingDrill.objects.create(training=t2, name_override="D2", order=2, weight=1)

		# a2 improves a lot; a1 regresses
		DrillScore.objects.create(training_drill=d1_t2, athlete=self.a1, score=7, rated_by=self.coach)
		DrillScore.objects.create(training_drill=d2_t2, athlete=self.a1, score=5, rated_by=self.coach)

		DrillScore.objects.create(training_drill=d1_t2, athlete=self.a2, score=9, rated_by=self.coach)
		DrillScore.objects.create(training_drill=d2_t2, athlete=self.a2, score=7, rated_by=self.coach)

		DrillScore.objects.create(training_drill=d1_t2, athlete=self.a3, score=6, rated_by=self.coach)
		DrillScore.objects.create(training_drill=d2_t2, athlete=self.a3, score=6, rated_by=self.coach)

		DrillScore.objects.create(training_drill=d1_t2, athlete=self.a4, score=4, rated_by=self.coach)
		DrillScore.objects.create(training_drill=d2_t2, athlete=self.a4, score=7, rated_by=self.coach)

		res = self.client.get("/api/trainings/evolution/?limit=2")
		self.assertEqual(res.status_code, 200)
		payload = res.json()
		self.assertIn("team_trend", payload)

		cmp_ = payload["comparison"]
		self.assertIsNotNone(cmp_)
		self.assertEqual(cmp_["biggest_improvement"]["athlete_name"], "A2")
		self.assertEqual(cmp_["biggest_regression"]["athlete_name"], "A1")
