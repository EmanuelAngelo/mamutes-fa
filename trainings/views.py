import csv
from django.http import HttpResponse
from django.db.models import Avg, Sum, Count, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from math import ceil, sqrt
from collections import defaultdict
from django.conf import settings
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
)
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

from accounts.permissions import IsAdminOrCoach
from .models import TrainingSession, Attendance, DrillCatalog, TrainingDrill, DrillScore
from .serializers import (
    TrainingSessionSerializer,
    AttendanceSerializer,
    DrillCatalogSerializer,
    TrainingDrillSerializer,
    DrillScoreSerializer,
)


class DrillCatalogViewSet(ModelViewSet):
    queryset = DrillCatalog.objects.all().order_by("name")
    serializer_class = DrillCatalogSerializer
    filterset_fields = ("category",)
    search_fields = ("name", "description")
    ordering_fields = ("name",)

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdminOrCoach()]
        return [IsAuthenticated()]


class TrainingSessionViewSet(ModelViewSet):
    queryset = TrainingSession.objects.all().order_by("-date")
    serializer_class = TrainingSessionSerializer
    filterset_fields = ("date", "location")
    search_fields = ("location", "notes")
    ordering_fields = ("date", "created_at")

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdminOrCoach()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # ----------------------------
    # BULK endpoints já existentes
    # ----------------------------
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsAdminOrCoach])
    def attendance_bulk(self, request, pk=None):
        training = self.get_object()
        results = []

        for item in request.data:
            obj, _created = Attendance.objects.update_or_create(
                training=training,
                athlete_id=item["athlete"],
                defaults={
                    "status": item.get("status", "PRESENT"),
                    "checkin_time": item.get("checkin_time"),
                },
            )
            results.append(obj)

        return Response(AttendanceSerializer(results, many=True).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsAdminOrCoach])
    def drills_bulk(self, request, pk=None):
        training = self.get_object()
        created = []
        for item in request.data:
            created.append(TrainingDrill.objects.create(
                training=training,
                drill_id=item.get("drill"),
                name_override=item.get("name_override"),
                order=item.get("order", 1),
                description=item.get("description"),
                max_score=item.get("max_score", 10),
                weight=item.get("weight", 1.0),
            ))
        return Response(TrainingDrillSerializer(created, many=True).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsAdminOrCoach])
    def scores_bulk(self, request, pk=None):
        saved = []
        for item in request.data:
            obj, _created = DrillScore.objects.update_or_create(
                training_drill_id=item["training_drill"],
                athlete_id=item["athlete"],
                defaults={
                    "score": item["score"],
                    "comment": item.get("comment"),
                    "rated_by": request.user,
                },
            )
            saved.append(obj)
        return Response(DrillScoreSerializer(saved, many=True).data)

    # ==========================================================
    # Helpers (ranking/dashboard)
    # ==========================================================
    def _get_rankable_attendances(self, training, position_code=None):
        qs = Attendance.objects.filter(
            training=training,
            status__in=["PRESENT", "LATE"],
        ).select_related("athlete")
        if position_code:
            qs = qs.filter(athlete__current_position=position_code)
        return qs

    def _compute_ranking_items(self, training, position_code=None):
        """
        Retorna items de ranking com tie-break:
            1) weighted_average desc
            2) scored_drills_count desc
            3) weighted_points (numerator) desc
            4) athlete_name asc
        """
        attendances = self._get_rankable_attendances(training, position_code=position_code)
        athlete_ids = list(attendances.values_list("athlete_id", flat=True))

        if not athlete_ids:
            return []

        status_map = {a.athlete_id: a.status for a in attendances}

        numerator_expr = ExpressionWrapper(
            F("score") * F("training_drill__weight"),
            output_field=FloatField(),
        )

        agg = (
            DrillScore.objects
            .filter(training_drill__training=training, athlete_id__in=athlete_ids)
            .values(
                "athlete_id",
                "athlete__name",
                "athlete__jersey_number",
                "athlete__current_position",
            )
            .annotate(
                weighted_points=Coalesce(Sum(numerator_expr), 0.0),
                weight_sum=Coalesce(Sum(F("training_drill__weight"), output_field=FloatField()), 0.0),
                scored_drills_count=Count("training_drill_id"),
            )
        )

        items = []
        for row in agg:
            denom = float(row["weight_sum"] or 0.0)
            wavg = round(float(row["weighted_points"]) / denom, 2) if denom > 0 else None

            items.append({
                "athlete_id": row["athlete_id"],
                "athlete_name": row["athlete__name"],
                "jersey_number": row["athlete__jersey_number"],
                "position": row["athlete__current_position"],
                "attendance_status": status_map.get(row["athlete_id"]),
                "weighted_average": wavg,
                "scored_drills_count": int(row["scored_drills_count"] or 0),
                "weighted_points": round(float(row["weighted_points"] or 0.0), 3),
            })

        items.sort(
            key=lambda x: (
                x["weighted_average"] is None,
                -(x["weighted_average"] or -9999),
                -x["scored_drills_count"],
                -x["weighted_points"],
                x["athlete_name"].lower() if x["athlete_name"] else "",
            )
        )

        for i, it in enumerate(items, start=1):
            it["rank"] = i

        return items

    def _get_drills_and_scores(self, training):
        drills = list(TrainingDrill.objects.filter(training=training).order_by("order", "id"))
        drill_ids = [d.id for d in drills]
        scores = list(
            DrillScore.objects
            .filter(training_drill_id__in=drill_ids)
            .select_related("athlete", "training_drill", "training_drill__drill")
        )
        return drills, scores

    def _mean(self, values):
        if not values:
            return None
        return float(sum(values) / len(values))

    def _variance(self, values):
        if not values:
            return None
        mu = self._mean(values)
        if mu is None:
            return None
        return float(sum((x - mu) ** 2 for x in values) / len(values))

    def _stddev(self, values):
        var = self._variance(values)
        return float(sqrt(var)) if var is not None else None

    def _weighted_averages(self, training, position_code=None):
        items = self._compute_ranking_items(training, position_code=position_code)
        return [x for x in items if x.get("weighted_average") is not None]

    def _score_distribution(self, training):
        scores = list(
            DrillScore.objects
            .filter(training_drill__training=training)
            .values_list("score", flat=True)
        )

        values = [float(s) for s in scores if s is not None]
        total = len(values)
        bins = [
            {"key": "0-4", "label": "0–4", "count": 0},
            {"key": "5-6", "label": "5–6", "count": 0},
            {"key": "7-8", "label": "7–8", "count": 0},
            {"key": "9-10", "label": "9–10", "count": 0},
        ]

        for v in values:
            if v < 5:
                bins[0]["count"] += 1
            elif v < 7:
                bins[1]["count"] += 1
            elif v < 9:
                bins[2]["count"] += 1
            else:
                bins[3]["count"] += 1

        for b in bins:
            b["percent"] = round((b["count"] / total) * 100.0, 2) if total else 0.0

        return {"total_scores": total, "bins": bins}

    def _drill_averages(self, training):
        drills = list(TrainingDrill.objects.filter(training=training).order_by("order", "id"))
        drill_avg_qs = (
            DrillScore.objects
            .filter(training_drill__training=training)
            .values("training_drill_id")
            .annotate(avg_score=Avg("score"), scores_count=Count("id"))
        )
        avg_map = {
            row["training_drill_id"]: {
                "avg": (float(row["avg_score"]) if row["avg_score"] is not None else None),
                "count": int(row["scores_count"] or 0),
            }
            for row in drill_avg_qs
        }

        items = []
        for d in drills:
            meta = avg_map.get(d.id, {"avg": None, "count": 0})
            items.append({
                "training_drill_id": d.id,
                "name": d.name,
                "order": d.order,
                "avg_score": round(meta["avg"], 2) if meta["avg"] is not None else None,
                "scores_count": meta["count"],
            })

        valid = [x for x in items if x["avg_score"] is not None and x["scores_count"] > 0]
        hardest = min(valid, key=lambda x: x["avg_score"]) if valid else None

        return items, hardest

    def _most_consistent_athlete(self, training):
        qs = (
            DrillScore.objects
            .filter(training_drill__training=training)
            .select_related("athlete")
            .values("athlete_id", "athlete__name")
        )

        bucket = defaultdict(list)
        athlete_name = {}
        for row in qs:
            athlete_name[row["athlete_id"]] = row["athlete__name"]

        for s in DrillScore.objects.filter(training_drill__training=training).values("athlete_id", "score"):
            if s["score"] is None:
                continue
            bucket[s["athlete_id"]].append(float(s["score"]))

        best = None
        for athlete_id, values in bucket.items():
            if len(values) < 2:
                continue
            var = self._variance(values)
            if var is None:
                continue
            item = {
                "athlete_id": athlete_id,
                "athlete_name": athlete_name.get(athlete_id),
                "variance": round(float(var), 4),
                "stddev": round(float(sqrt(var)), 4),
                "scored_drills": len(values),
            }
            if best is None or item["variance"] < best["variance"]:
                best = item

        return best

    # ==========================================================
    # Endpoints
    # ==========================================================
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated, IsAdminOrCoach])
    def ranking(self, request, pk=None):
        training = self.get_object()
        position = request.query_params.get("position")  # ex: WR, DB, QB...
        items = self._compute_ranking_items(training, position_code=position)

        return Response({
            "training": {
                "id": training.id,
                "date": training.date,
                "start_time": training.start_time,
                "location": training.location,
            },
            "filters": {"position": position},
            "items": items,
        })

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated, IsAdminOrCoach])
    def coach_dashboard(self, request, pk=None):
        training = self.get_object()

        attendances = (
            Attendance.objects
            .filter(training=training)
            .select_related("athlete")
            .order_by("athlete__name")
        )
        attendance_payload = [{
            "athlete_id": a.athlete_id,
            "athlete_name": a.athlete.name,
            "jersey_number": a.athlete.jersey_number,
            "position": a.athlete.current_position,
            "status": a.status,
            "checkin_time": a.checkin_time,
        } for a in attendances]

        drills, scores = self._get_drills_and_scores(training)

        drills_payload = [{
            "training_drill_id": d.id,
            "name": d.name,
            "order": d.order,
            "max_score": d.max_score,
            "weight": float(d.weight),
            "description": d.description,
        } for d in drills]

        drill_avg_qs = (
            DrillScore.objects
            .filter(training_drill__training=training)
            .values("training_drill_id")
            .annotate(avg_score=Avg("score"))
        )
        drill_avg_map = {
            row["training_drill_id"]: (
                round(float(row["avg_score"]), 2) if row["avg_score"] is not None else None
            )
            for row in drill_avg_qs
        }
        for d in drills_payload:
            d["average_score"] = drill_avg_map.get(d["training_drill_id"])

        # JSON-safe map: {"<athlete_id>": {"<training_drill_id>": {score, comment, rated_by}}}
        score_map = {}
        for s in scores:
            athlete_key = str(s.athlete_id)
            drill_key = str(s.training_drill_id)
            if athlete_key not in score_map:
                score_map[athlete_key] = {}
            score_map[athlete_key][drill_key] = {
                "score": float(s.score),
                "comment": s.comment,
                "rated_by": s.rated_by_id,
            }

        ranking_items = self._compute_ranking_items(training)
        valid_avgs = [x["weighted_average"] for x in ranking_items if x["weighted_average"] is not None]
        training_weighted_avg = round(sum(valid_avgs) / len(valid_avgs), 2) if valid_avgs else None

        rankable_positions = list(
            Attendance.objects
            .filter(training=training, status__in=["PRESENT", "LATE"])
            .exclude(athlete__current_position__isnull=True)
            .exclude(athlete__current_position__exact="")
            .values_list("athlete__current_position", flat=True)
            .distinct()
        )
        ranking_by_position = {pos: self._compute_ranking_items(training, position_code=pos) for pos in rankable_positions}

        return Response({
            "training": {
                "id": training.id,
                "date": training.date,
                "start_time": training.start_time,
                "location": training.location,
                "notes": training.notes,
            },
            "summary": {
                "athletes_total": len(attendance_payload),
                "drills_total": len(drills_payload),
                "training_weighted_average": training_weighted_avg,
            },
            "attendance": attendance_payload,
            "drills": drills_payload,
            "ranking": ranking_items,
            "ranking_by_position": ranking_by_position,
            "score_map": score_map,
        })

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated, IsAdminOrCoach])
    def coach_overview(self, request):
        """Resumo para gráficos do Coach Dashboard (tendência + último treino)."""
        try:
            limit = int(request.query_params.get("limit", "8"))
        except ValueError:
            limit = 8
        limit = max(1, min(limit, 30))

        latest_qs = TrainingSession.objects.all().order_by("-date", "-id")
        latest = latest_qs.first()

        trend_trainings = list(latest_qs[:limit])
        trend_trainings.reverse()  # chronological

        trend_items = []
        for t in trend_trainings:
            ranking_items = self._compute_ranking_items(t)
            valid_avgs = [x["weighted_average"] for x in ranking_items if x["weighted_average"] is not None]
            training_weighted_avg = round(sum(valid_avgs) / len(valid_avgs), 2) if valid_avgs else 0
            trend_items.append({
                "label": str(t.date),
                "value": float(training_weighted_avg),
            })

        latest_drills_items = []
        latest_training_payload = None
        if latest:
            drills = list(TrainingDrill.objects.filter(training=latest).order_by("order", "id"))
            drill_avg_qs = (
                DrillScore.objects
                .filter(training_drill__training=latest)
                .values("training_drill_id")
                .annotate(avg_score=Avg("score"))
            )
            drill_avg_map = {
                row["training_drill_id"]: (
                    round(float(row["avg_score"]), 2) if row["avg_score"] is not None else 0
                )
                for row in drill_avg_qs
            }

            for d in drills:
                latest_drills_items.append({
                    "label": d.name,
                    "value": float(drill_avg_map.get(d.id, 0)),
                })

            ranking_items = self._compute_ranking_items(latest)
            valid_avgs = [x["weighted_average"] for x in ranking_items if x["weighted_average"] is not None]
            latest_training_weighted_avg = round(sum(valid_avgs) / len(valid_avgs), 2) if valid_avgs else None

            latest_training_payload = {
                "id": latest.id,
                "date": latest.date,
                "location": latest.location,
                "training_weighted_average": latest_training_weighted_avg,
            }

        return Response({
            "trend": trend_items,
            "latest_training": latest_training_payload,
            "latest_drills": latest_drills_items,
        })

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated, IsAdminOrCoach])
    def analytics(self, request, pk=None):
        """Métricas analíticas avançadas por treino (visão coach)."""
        training = self.get_object()

        # Weighted averages (ranking)
        ranked = self._weighted_averages(training)
        wavg_values = [float(x["weighted_average"]) for x in ranked]
        wavg_mean = self._mean(wavg_values)
        wavg_std = self._stddev(wavg_values)

        # Top3 vs Bottom3 gap
        top = wavg_values[:3]
        bottom = wavg_values[-3:] if len(wavg_values) >= 3 else wavg_values
        top_mean = self._mean(top)
        bottom_mean = self._mean(bottom)
        top_bottom_gap = (top_mean - bottom_mean) if (top_mean is not None and bottom_mean is not None) else None

        # Position stats
        by_pos = defaultdict(list)
        for it in ranked:
            by_pos[it.get("position") or ""] .append(float(it["weighted_average"]))

        pos_items = []
        for pos, vals in by_pos.items():
            if not vals:
                continue
            avg = self._mean(vals)
            gap_internal = (max(vals) - min(vals)) if len(vals) >= 2 else 0.0
            pos_items.append({
                "position": pos or None,
                "athletes_count": len(vals),
                "avg_weighted": round(avg, 2) if avg is not None else None,
                "internal_gap": round(float(gap_internal), 2),
            })
        pos_items.sort(key=lambda x: (x["position"] is None, x["position"] or ""))

        # Drill averages + hardest drill
        drill_items, hardest = self._drill_averages(training)

        # Score distribution (all DrillScore in training)
        distribution = self._score_distribution(training)

        # Most consistent athlete (lowest variance across drills)
        most_consistent = self._most_consistent_athlete(training)

        return Response({
            "training": {"id": training.id, "date": training.date},
            "distribution": distribution,
            "weighted_average": {
                "athletes_count": len(wavg_values),
                "mean": round(wavg_mean, 2) if wavg_mean is not None else None,
                "stddev": round(wavg_std, 4) if wavg_std is not None else None,
            },
            "top3_bottom3_gap": {
                "top3_mean": round(top_mean, 2) if top_mean is not None else None,
                "bottom3_mean": round(bottom_mean, 2) if bottom_mean is not None else None,
                "gap": round(top_bottom_gap, 2) if top_bottom_gap is not None else None,
            },
            "by_position": pos_items,
            "by_drill": drill_items,
            "hardest_drill": hardest,
            "most_consistent_athlete": most_consistent,
        })

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated, IsAdminOrCoach])
    def evolution(self, request):
        """Métricas evolutivas (time e atletas) para o Coach Dashboard."""
        try:
            limit = int(request.query_params.get("limit", "8"))
        except ValueError:
            limit = 8
        limit = max(2, min(limit, 30))

        athlete_id = request.query_params.get("athlete_id")
        athlete_id = int(athlete_id) if athlete_id and athlete_id.isdigit() else None

        latest_qs = TrainingSession.objects.all().order_by("-date", "-id")
        trainings = list(latest_qs[:limit])
        trainings.reverse()  # chronological

        team_trend = []
        per_training_athlete_avg = []  # list of dict athlete_id -> wavg
        for t in trainings:
            ranked = self._weighted_averages(t)
            values = [float(x["weighted_average"]) for x in ranked]
            team_avg = self._mean(values)
            team_trend.append({
                "training_id": t.id,
                "label": str(t.date),
                "value": float(round(team_avg, 2)) if team_avg is not None else 0.0,
            })
            per_training_athlete_avg.append({x["athlete_id"]: float(x["weighted_average"]) for x in ranked})

        from_t = trainings[-2] if len(trainings) >= 2 else None
        to_t = trainings[-1] if trainings else None

        comparison = None
        athletes_summary = []

        if from_t and to_t:
            from_map = per_training_athlete_avg[-2]
            to_map = per_training_athlete_avg[-1]
            common_ids = set(from_map.keys()) & set(to_map.keys())

            name_map = {x["athlete_id"]: x.get("athlete_name") for x in self._weighted_averages(to_t)}
            name_map.update({x["athlete_id"]: x.get("athlete_name") for x in self._weighted_averages(from_t)})

            for aid in common_ids:
                delta = float(to_map[aid] - from_map[aid])
                athletes_summary.append({
                    "athlete_id": aid,
                    "athlete_name": name_map.get(aid),
                    "from": round(float(from_map[aid]), 2),
                    "to": round(float(to_map[aid]), 2),
                    "delta": round(delta, 2),
                })

            best = max(athletes_summary, key=lambda x: x["delta"], default=None)
            worst = min(athletes_summary, key=lambda x: x["delta"], default=None)

            comparison = {
                "from_training": {"id": from_t.id, "date": from_t.date},
                "to_training": {"id": to_t.id, "date": to_t.date},
                "biggest_improvement": best,
                "biggest_regression": worst,
            }

        individual = None
        if athlete_id:
            series = []
            for idx, t in enumerate(trainings):
                val = per_training_athlete_avg[idx].get(athlete_id)
                series.append({
                    "training_id": t.id,
                    "label": str(t.date),
                    "value": round(float(val), 2) if val is not None else None,
                })
            individual = {"athlete_id": athlete_id, "trend": series}

        return Response({
            "trainings": [{"id": t.id, "date": t.date} for t in trainings],
            "team_trend": team_trend,
            "comparison": comparison,
            "athletes_summary": athletes_summary,
            "individual": individual,
        })

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated, IsAdminOrCoach], url_path="export/pdf")
    def export_pdf(self, request, pk=None):
        return _export_pdf_impl(self, request, pk)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated, IsAdminOrCoach], url_path="export/csv")
    def export_csv(self, request, pk=None):
        return _export_csv_impl(self, request, pk)
    
def _export_pdf_impl(self, request, pk=None):
    training = self.get_object()

    # =============================
    # Coleta dados (reuso helpers)
    # =============================
    drills, scores = self._get_drills_and_scores(training)
    drills_sorted = sorted(drills, key=lambda d: (d.order, d.id))

    attendances = (
        Attendance.objects
        .filter(training=training)
        .select_related("athlete")
        .order_by("athlete__name")
    )

    # Ranking geral + por posição (já com tie-break + ponderada)
    ranking_items = self._compute_ranking_items(training)

    # ranking_by_position (apenas posições presentes/atraso)
    rankable_positions = list(
        Attendance.objects
        .filter(training=training, status__in=["PRESENT", "LATE"])
        .exclude(athlete__current_position__isnull=True)
        .exclude(athlete__current_position__exact="")
        .values_list("athlete__current_position", flat=True)
        .distinct()
    )
    ranking_by_position = {pos: self._compute_ranking_items(training, position_code=pos) for pos in rankable_positions}

    # score_map: (athlete_id, drill_id) -> (score, comment)
    score_map = {}
    for s in scores:
        score_map[(s.athlete_id, s.training_drill_id)] = (float(s.score), s.comment or "")

    ranking_map = {r["athlete_id"]: r for r in ranking_items}

    # Resumo
    total_athletes = attendances.count()
    present_count = attendances.filter(status__in=["PRESENT", "LATE"]).count()
    absent_count = attendances.filter(status="ABSENT").count()
    justified_count = attendances.filter(status="JUSTIFIED").count()
    drills_total = len(drills_sorted)

    valid_avgs = [x["weighted_average"] for x in ranking_items if x["weighted_average"] is not None]
    training_weighted_avg = round(sum(valid_avgs) / len(valid_avgs), 2) if valid_avgs else None

    # =============================
    # PDF setup
    # =============================
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.0 * cm,
        bottomMargin=1.0 * cm,
        title=f"Relatório de Treino {training.date}",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleX", fontSize=20, leading=22, spaceAfter=10))
    styles.add(ParagraphStyle(name="H1X", fontSize=14, leading=16, spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name="H2X", fontSize=11, leading=13, spaceBefore=8, spaceAfter=5))
    styles.add(ParagraphStyle(name="SmallX", fontSize=9, leading=11))
    styles.add(ParagraphStyle(name="TinyX", fontSize=8, leading=10))

    brand_name = getattr(settings, "BRAND_NAME", "Mamutes F.A.")
    logo_path = getattr(settings, "BRAND_LOGO_PATH", None)

    def tstyle(header_bg="#F0F0F0"):
        return TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9C9C9")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ])

    def page_footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(landscape(A4)[0] - doc_.rightMargin, 0.75*cm, f"Página {doc_.page}")
        canvas.restoreState()

    def safe_logo():
        if not logo_path:
            return None
        try:
            img = Image(str(logo_path))
            img.drawHeight = 2.2 * cm
            img.drawWidth = 2.2 * cm
            return img
        except Exception:
            return None

    # =============================
    # Charts (Top N bar chart)
    # =============================
    def build_top_bar_chart(items, top_n=10):
        """
        Bar chart Top N (weighted_average). Itens já ordenados.
        """
        top = [x for x in items if x["weighted_average"] is not None][:top_n]
        if not top:
            return None

        labels = [x["athlete_name"][:12] for x in top]  # curta pra caber
        values = [x["weighted_average"] for x in top]

        d = Drawing(26*cm, 7.2*cm)

        title = String(0, 6.8*cm, f"Top {len(top)} - Média Ponderada (0–10)", fontName="Helvetica-Bold", fontSize=10)
        d.add(title)

        chart = VerticalBarChart()
        chart.x = 0.5*cm
        chart.y = 0.8*cm
        chart.height = 5.6*cm
        chart.width = 25*cm
        chart.data = [values]
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 10
        chart.valueAxis.valueStep = 1

        chart.categoryAxis.categoryNames = labels
        chart.categoryAxis.labels.fontName = "Helvetica"
        chart.categoryAxis.labels.fontSize = 7
        chart.categoryAxis.labels.angle = 30
        chart.categoryAxis.labels.dy = -10

        # estilo neutro
        chart.bars[0].fillColor = colors.HexColor("#4F81BD")
        chart.valueAxis.labels.fontSize = 8
        chart.valueAxis.labels.fontName = "Helvetica"

        d.add(chart)
        return d

    # =============================
    # Drill columns chunking (smart split)
    # =============================
    def calc_max_drills_per_page():
        # Larguras base (fixas)
        base_widths = [7.0*cm, 1.6*cm, 1.8*cm, 2.4*cm, 2.4*cm, 1.2*cm]  # atleta, camisa, pos, status, média, rank
        page_width = landscape(A4)[0] - (doc.leftMargin + doc.rightMargin)

        # Cada drill vira 2 colunas (nota + coment) → coment é maior
        # Mas no nosso layout por página, vamos mostrar:
        #   - colunas fixas
        #   - N drills (nota)
        #   - N drills (coment)
        # Para caber, limitamos N por página
        remaining_width = max(page_width - sum(base_widths), 10*cm)

        # “custo” por drill = (nota_col + comment_col)
        # nota pequena, comment média
        per_drill = (1.2*cm + 2.8*cm)  # ~4.0cm
        max_n = int(remaining_width // per_drill)
        return max(1, min(max_n, 10))  # no máximo 10 drills por página pra manter legível

    max_drills_page = calc_max_drills_per_page()

    def chunk_list(lst, size):
        for i in range(0, len(lst), size):
            yield lst[i:i+size]

    # =============================
    # Build PDF story
    # =============================
    story = []

    # -------- Capa --------
    logo = safe_logo()
    cover_bits = []
    if logo:
        cover_bits.append(logo)
        cover_bits.append(Spacer(1, 8))

    cover_bits.append(Paragraph(f"{brand_name}", styles["TitleX"]))
    cover_bits.append(Paragraph("Relatório Premium de Treino", styles["H1X"]))
    cover_bits.append(Spacer(1, 6))
    cover_bits.append(Paragraph(
        f"<b>Data:</b> {training.date} &nbsp;&nbsp; "
        f"<b>Horário:</b> {training.start_time or '-'} &nbsp;&nbsp; "
        f"<b>Local:</b> {training.location or '-'}",
        styles["Normal"]
    ))
    if training.notes:
        cover_bits.append(Spacer(1, 6))
        cover_bits.append(Paragraph(f"<b>Observações:</b> {training.notes}", styles["SmallX"]))

    cover_bits.append(Spacer(1, 14))
    cover_bits.append(Paragraph(
        f"<b>Resumo rápido:</b> "
        f"Atletas={total_athletes} | Presentes/Atraso={present_count} | "
        f"Ausentes={absent_count} | Justificados={justified_count} | "
        f"Drills={drills_total} | "
        f"Média ponderada do treino={training_weighted_avg if training_weighted_avg is not None else '-'}",
        styles["Normal"]
    ))

    story.append(KeepTogether(cover_bits))
    story.append(PageBreak())

    # -------- Sumário executivo + Top 3 --------
    story.append(Paragraph("Sumário Executivo", styles["H1X"]))

    sum_table = Table([[
        "Atletas", "Presentes/Atraso", "Ausentes", "Justificados", "Drills", "Média Ponderada"
    ], [
        str(total_athletes),
        str(present_count),
        str(absent_count),
        str(justified_count),
        str(drills_total),
        str(training_weighted_avg) if training_weighted_avg is not None else "-"
    ]], repeatRows=1)
    sum_table.setStyle(tstyle(header_bg="#E8F0FE"))
    story.append(sum_table)
    story.append(Spacer(1, 10))

    # Top 3 geral
    story.append(Paragraph("Top 3 Geral (média ponderada + desempate)", styles["H2X"]))
    top3 = ranking_items[:3]
    top3_data = [["Rank", "Atleta", "Camisa", "Posição", "Média", "Drills", "Pontos"]]
    for r in top3:
        top3_data.append([
            r.get("rank", ""), r.get("athlete_name", ""),
            r.get("jersey_number", "") or "",
            r.get("position", "") or "",
            r.get("weighted_average", "") if r.get("weighted_average") is not None else "",
            r.get("scored_drills_count", ""),
            r.get("weighted_points", ""),
        ])
    ttop = Table(top3_data, repeatRows=1)
    ttop.setStyle(tstyle(header_bg="#E6FFE6"))
    story.append(ttop)
    story.append(Spacer(1, 10))

    # Top 3 por posição
    story.append(Paragraph("Top 3 por Posição", styles["H2X"]))
    pos_rows = [["Posição", "1º", "2º", "3º"]]
    for pos, items in sorted(ranking_by_position.items(), key=lambda x: x[0]):
        names = [f'{x["athlete_name"]} ({x["weighted_average"]})' if x["weighted_average"] is not None else x["athlete_name"] for x in items[:3]]
        while len(names) < 3:
            names.append("-")
        pos_rows.append([pos, names[0], names[1], names[2]])

    tpos = Table(pos_rows, repeatRows=1)
    tpos.setStyle(tstyle(header_bg="#FFF2CC"))
    story.append(tpos)
    story.append(Spacer(1, 12))

    # Gráfico Top N
    chart = build_top_bar_chart(ranking_items, top_n=10)
    if chart:
        story.append(Paragraph("Gráfico", styles["H2X"]))
        story.append(chart)
        story.append(Spacer(1, 8))

    story.append(PageBreak())

    # -------- Presença --------
    story.append(Paragraph("Presença", styles["H1X"]))
    attendance_data = [["Atleta", "Camisa", "Posição", "Status", "Check-in"]]
    for a in attendances:
        attendance_data.append([
            a.athlete.name,
            a.athlete.jersey_number or "",
            a.athlete.current_position or "",
            a.status,
            a.checkin_time or "",
        ])
    t_att = Table(attendance_data, repeatRows=1)
    t_att.setStyle(tstyle())
    story.append(t_att)
    story.append(PageBreak())

    # -------- Ranking completo --------
    story.append(Paragraph("Ranking Completo (ponderado + desempate)", styles["H1X"]))
    ranking_data = [["Rank", "Atleta", "Camisa", "Posição", "Média ponderada", "Drills avaliados", "Pontos ponderados"]]
    for r in ranking_items:
        ranking_data.append([
            r.get("rank", ""),
            r.get("athlete_name", ""),
            r.get("jersey_number", "") or "",
            r.get("position", "") or "",
            r.get("weighted_average", "") if r.get("weighted_average") is not None else "",
            r.get("scored_drills_count", ""),
            r.get("weighted_points", ""),
        ])
    t_rank = Table(ranking_data, repeatRows=1)
    t_rank.setStyle(tstyle())
    story.append(t_rank)
    story.append(PageBreak())

    # -------- Notas por Drill (smart split por colunas) --------
    story.append(Paragraph("Notas por Drill (com comentários)", styles["H1X"]))
    story.append(Paragraph(
        f"Quando há muitos drills, o relatório divide em {max_drills_page} drills por página (nota + comentário).",
        styles["SmallX"]
    ))
    story.append(Spacer(1, 8))

    # Para cada “chunk” de drills, gera uma tabela
    drill_chunks = list(chunk_list(drills_sorted, max_drills_page))
    total_chunks = len(drill_chunks)

    for idx, chunk in enumerate(drill_chunks, start=1):
        story.append(Paragraph(f"Bloco {idx}/{total_chunks}", styles["H2X"]))

        headers = ["Atleta", "Camisa", "Posição", "Status", "Média", "Rank"]
        for d in chunk:
            headers.append(f"{d.name} (nota)")
        for d in chunk:
            headers.append(f"{d.name} (coment.)")

        rows = [headers]

        for a in attendances:
            athlete = a.athlete
            r = ranking_map.get(athlete.id, {})
            base = [
                athlete.name,
                athlete.jersey_number or "",
                athlete.current_position or "",
                a.status,
                r.get("weighted_average", "") if r.get("weighted_average") is not None else "",
                r.get("rank", ""),
            ]

            scores_row = []
            comments_row = []
            for d in chunk:
                sc, comment = score_map.get((athlete.id, d.id), ("", ""))
                scores_row.append(sc)

                # comentário “legível”
                if isinstance(comment, str):
                    comment_txt = comment.strip()
                    comment_txt = (comment_txt[:120] + "...") if len(comment_txt) > 123 else comment_txt
                else:
                    comment_txt = ""
                comments_row.append(comment_txt)

            rows.append(base + scores_row + comments_row)

        # Larguras (fixas + distribui)
        base_widths = [7.0*cm, 1.6*cm, 1.8*cm, 2.4*cm, 2.0*cm, 1.2*cm]
        page_width = landscape(A4)[0] - (doc.leftMargin + doc.rightMargin)
        remaining_cols = len(headers) - len(base_widths)
        remaining_width = max(page_width - sum(base_widths), 10*cm)
        each = remaining_width / max(remaining_cols, 1)
        col_widths = base_widths + [each] * remaining_cols

        t_notes = Table(rows, colWidths=col_widths, repeatRows=1)
        t_notes.setStyle(tstyle())
        story.append(t_notes)

        if idx < total_chunks:
            story.append(PageBreak())

    # Build
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="treino_{training.id}_{training.date}_premium.pdf"'
    response.write(pdf)
    return response

    # ==========================================================
    # Helpers
    # ==========================================================
def _get_rankable_attendances(self, training, position_code=None):
    qs = Attendance.objects.filter(training=training, status__in=["PRESENT", "LATE"]).select_related("athlete")
    if position_code:
        qs = qs.filter(athlete__current_position=position_code)
    return qs

def _compute_ranking_items(self, training, position_code=None):
    """
    Retorna items de ranking com tie-break:
        1) weighted_average desc
        2) scored_drills_count desc
        3) weighted_points (numerator) desc
        4) athlete_name asc
    """
    attendances = self._get_rankable_attendances(training, position_code=position_code)
    athlete_ids = list(attendances.values_list("athlete_id", flat=True))

    if not athlete_ids:
        return []

    status_map = {a.athlete_id: a.status for a in attendances}

    numerator_expr = ExpressionWrapper(
        F("score") * F("training_drill__weight"),
        output_field=FloatField()
    )

    agg = (
        DrillScore.objects
        .filter(training_drill__training=training, athlete_id__in=athlete_ids)
        .values(
            "athlete_id",
            "athlete__name",
            "athlete__jersey_number",
            "athlete__current_position",
        )
        .annotate(
            weighted_points=Coalesce(Sum(numerator_expr), 0.0),
            weight_sum=Coalesce(Sum(F("training_drill__weight"), output_field=FloatField()), 0.0),
            scored_drills_count=Coalesce(Sum(1, output_field=FloatField()), 0.0),
        )
    )

    items = []
    for row in agg:
        denom = float(row["weight_sum"] or 0.0)
        wavg = round(float(row["weighted_points"]) / denom, 2) if denom > 0 else None

        items.append({
            "athlete_id": row["athlete_id"],
            "athlete_name": row["athlete__name"],
            "jersey_number": row["athlete__jersey_number"],
            "position": row["athlete__current_position"],
            "attendance_status": status_map.get(row["athlete_id"]),
            "weighted_average": wavg,
            "scored_drills_count": int(row["scored_drills_count"] or 0),
            "weighted_points": round(float(row["weighted_points"] or 0.0), 3),
        })

    # Tie-break sorting
    # None average goes last
    items.sort(key=lambda x: (
        x["weighted_average"] is None,
        -(x["weighted_average"] or -9999),
        -x["scored_drills_count"],
        -x["weighted_points"],
        x["athlete_name"].lower() if x["athlete_name"] else "",
    ))

    for i, it in enumerate(items, start=1):
        it["rank"] = i

    return items

def _get_drills_and_scores(self, training):
    drills = list(TrainingDrill.objects.filter(training=training).order_by("order", "id"))
    drill_ids = [d.id for d in drills]
    scores = list(
        DrillScore.objects
        .filter(training_drill_id__in=drill_ids)
        .select_related("athlete", "training_drill", "training_drill__drill")
    )
    return drills, scores

# ==========================================================
# NOVO: Ranking (com tie-break) + filtro por posição
# ==========================================================
@action(detail=True, methods=["get"], permission_classes=[IsAuthenticated, IsAdminOrCoach])
def ranking(self, request, pk=None):
    training = self.get_object()
    position = request.query_params.get("position")  # ex: WR, DB, QB...

    items = self._compute_ranking_items(training, position_code=position)

    return Response({
        "training": {
            "id": training.id,
            "date": training.date,
            "start_time": training.start_time,
            "location": training.location,
        },
        "filters": {"position": position},
        "items": items,
    })

    # ==========================================================
    # NOVO: Dashboard do Coach (inclui ranking por posição)
    # ==========================================================
@action(detail=True, methods=["get"], permission_classes=[IsAuthenticated, IsAdminOrCoach])
def coach_dashboard(self, request, pk=None):
    training = self.get_object()

    # Presença completa (todos, inclusive ausentes)
    attendances = (
        Attendance.objects
        .filter(training=training)
        .select_related("athlete")
        .order_by("athlete__name")
    )
    attendance_payload = [{
        "athlete_id": a.athlete_id,
        "athlete_name": a.athlete.name,
        "jersey_number": a.athlete.jersey_number,
        "position": a.athlete.current_position,
        "status": a.status,
        "checkin_time": a.checkin_time,
    } for a in attendances]

    drills, scores = self._get_drills_and_scores(training)

    drills_payload = [{
        "training_drill_id": d.id,
        "name": d.name,
        "order": d.order,
        "max_score": d.max_score,
        "weight": float(d.weight),
        "description": d.description,
    } for d in drills]

    # Média por drill
    drill_avg_qs = (
        DrillScore.objects
        .filter(training_drill__training=training)
        .values("training_drill_id")
        .annotate(avg_score=Avg("score"))
    )
    drill_avg_map = {row["training_drill_id"]: (round(float(row["avg_score"]), 2) if row["avg_score"] is not None else None) for row in drill_avg_qs}
    for d in drills_payload:
        d["average_score"] = drill_avg_map.get(d["training_drill_id"])

    # score_map (athlete_id, drill_id) => score/comment
    score_map = {}
    for s in scores:
        score_map[(s.athlete_id, s.training_drill_id)] = {
            "score": float(s.score),
            "comment": s.comment,
            "rated_by": s.rated_by_id,
        }

    # Ranking geral (tie-break + ponderada)
    ranking_items = self._compute_ranking_items(training)

    # Média ponderada geral do treino (média das médias dos atletas rankeados)
    valid_avgs = [x["weighted_average"] for x in ranking_items if x["weighted_average"] is not None]
    training_weighted_avg = round(sum(valid_avgs) / len(valid_avgs), 2) if valid_avgs else None

    # Ranking por posição
    # Pegamos as posições presentes no treino (rankáveis) e montamos um dict
    rankable_positions = list(
        Attendance.objects
        .filter(training=training, status__in=["PRESENT", "LATE"])
        .exclude(athlete__current_position__isnull=True)
        .exclude(athlete__current_position__exact="")
        .values_list("athlete__current_position", flat=True)
        .distinct()
    )
    ranking_by_position = {}
    for pos in rankable_positions:
        ranking_by_position[pos] = self._compute_ranking_items(training, position_code=pos)

    return Response({
        "training": {
            "id": training.id,
            "date": training.date,
            "start_time": training.start_time,
            "location": training.location,
            "notes": training.notes,
        },
        "summary": {
            "athletes_total": len(attendance_payload),
            "drills_total": len(drills_payload),
            "training_weighted_average": training_weighted_avg,
        },
        "attendance": attendance_payload,
        "drills": drills_payload,
        "ranking": ranking_items,
        "ranking_by_position": ranking_by_position,
        "score_map": score_map,
    })

# ==========================================================
# NOVO: Export CSV (abre no Excel)
# ==========================================================
def _export_csv_impl(self, request, pk=None):
        training = self.get_object()

        drills, scores = self._get_drills_and_scores(training)
        drills_sorted = sorted(drills, key=lambda d: (d.order, d.id))

        # Ranking geral (para rank e weighted_average)
        ranking_items = self._compute_ranking_items(training)
        ranking_map = {r["athlete_id"]: r for r in ranking_items}

        # Presença (todos)
        attendances = (
            Attendance.objects
            .filter(training=training)
            .select_related("athlete")
            .order_by("athlete__name")
        )

        # score_map
        score_map = {}
        for s in scores:
            score_map[(s.athlete_id, s.training_drill_id)] = (float(s.score), s.comment or "")

        # Header
        base_cols = [
            "athlete_name",
            "jersey_number",
            "position",
            "attendance_status",
            "weighted_average",
            "rank",
        ]
        drill_cols = []
        comment_cols = []
        for d in drills_sorted:
            drill_cols.append(f"Drill: {d.name}")
            comment_cols.append(f"Comment: {d.name}")

        columns = base_cols + drill_cols + comment_cols

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="treino_{training.id}_{training.date}.csv"'

        writer = csv.writer(response)
        writer.writerow(columns)

        for a in attendances:
            athlete = a.athlete
            r = ranking_map.get(athlete.id, {})
            row = [
                athlete.name,
                athlete.jersey_number or "",
                athlete.current_position or "",
                a.status,
                r.get("weighted_average", ""),
                r.get("rank", ""),
            ]

            # Scores
            for d in drills_sorted:
                sc, _cm = score_map.get((athlete.id, d.id), ("", ""))
                row.append(sc)

            # Comments
            for d in drills_sorted:
                _sc, cm = score_map.get((athlete.id, d.id), ("", ""))
                row.append(cm)

            writer.writerow(row)

        return response


class TrainingDrillViewSet(ModelViewSet):
    queryset = TrainingDrill.objects.all()
    serializer_class = TrainingDrillSerializer
    filterset_fields = ("training",)
    ordering_fields = ("order",)

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdminOrCoach()]
        return [IsAuthenticated()]


class DrillScoreViewSet(ModelViewSet):
    queryset = DrillScore.objects.all()
    serializer_class = DrillScoreSerializer
    filterset_fields = ("athlete", "training_drill")
    ordering_fields = ("created_at",)

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdminOrCoach()]
        return [IsAuthenticated()]