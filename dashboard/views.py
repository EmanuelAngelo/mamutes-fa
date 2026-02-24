from django.db.models import Avg, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from trainings.models import TrainingSession, Attendance, TrainingDrill, DrillScore


def get_my_athlete_or_404(user):
    athlete = getattr(user, "athlete", None)
    return athlete


class MyLatestTrainingView(APIView):
    """
    Último treino em que o atleta esteve PRESENT ou LATE, com drills e notas.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        athlete = get_my_athlete_or_404(request.user)
        if not athlete:
            return Response({"detail": "Usuário não vinculado a atleta."}, status=404)

        last_attendance = (
            Attendance.objects
            .filter(athlete=athlete, status__in=["PRESENT", "LATE"])
            .select_related("training")
            .order_by("-training__date", "-training__id")
            .first()
        )

        if not last_attendance:
            return Response({"detail": "Nenhum treino encontrado para este atleta."}, status=404)

        training = last_attendance.training

        drills = (
            TrainingDrill.objects
            .filter(training=training)
            .order_by("order", "id")
        )

        # Busca todas as notas do atleta nesse treino
        scores = (
            DrillScore.objects
            .filter(athlete=athlete, training_drill__training=training)
            .select_related("training_drill", "training_drill__drill")
        )

        score_map = {s.training_drill_id: s for s in scores}

        drill_payload = []
        for d in drills:
            s = score_map.get(d.id)
            drill_payload.append({
                "training_drill_id": d.id,
                "drill_name": d.name,
                "order": d.order,
                "max_score": d.max_score,
                "weight": float(d.weight),
                "score": float(s.score) if s else None,
                "comment": s.comment if s else None,
            })

        # Média simples do dia (considera só drills que têm nota)
        scored_values = [p["score"] for p in drill_payload if p["score"] is not None]
        # day_avg = round(sum(scored_values) / len(scored_values), 2) if scored_values else None
        # Média ponderada do dia (considera só drills que têm nota)
        numerator = 0.0
        denominator = 0.0
        for p in drill_payload:
            if p["score"] is not None:
                w = float(p["weight"] or 1.0)
                numerator += float(p["score"]) * w
                denominator += w

        day_weighted_avg = round(numerator / denominator, 2) if denominator > 0 else None

        return Response({
            "training": {
                "id": training.id,
                "date": training.date,
                "start_time": training.start_time,
                "location": training.location,
                "notes": training.notes,
            },
            "attendance_status": last_attendance.status,
            "day_weighted_average": day_weighted_avg,
            "drills": drill_payload,
        })


class MyDrillTrendsView(APIView):
    """
    Série temporal de notas por drill (para gráfico).
    Filtro por:
      - drill_catalog_id (quando TrainingDrill.drill != null)
      - ou name (quando usa name_override)
    Query params:
      ?drill_catalog_id=3
      ?name=Route%20Tree
      ?limit=20
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        athlete = get_my_athlete_or_404(request.user)
        if not athlete:
            return Response({"detail": "Usuário não vinculado a atleta."}, status=404)

        drill_catalog_id = request.query_params.get("drill_catalog_id")
        name = request.query_params.get("name")
        limit = int(request.query_params.get("limit", "20"))

        qs = (
            DrillScore.objects
            .filter(athlete=athlete)
            .select_related("training_drill", "training_drill__training", "training_drill__drill")
            .order_by("-training_drill__training__date", "-id")
        )

        if drill_catalog_id:
            qs = qs.filter(training_drill__drill_id=drill_catalog_id)
        elif name:
            qs = qs.filter(training_drill__name_override__iexact=name)
        else:
            return Response(
                {"detail": "Informe drill_catalog_id ou name para gerar tendência."},
                status=400,
            )

        qs = qs[:limit]
        # retornar em ordem crescente pro gráfico
        data = list(reversed([{
            "date": s.training_drill.training.date,
            "training_id": s.training_drill.training.id,
            "drill_name": s.training_drill.name,
            "score": float(s.score),
            "comment": s.comment,
        } for s in qs]))

        return Response({"items": data})


class MyImprovementsView(APIView):
    """
    Pontos de melhoria: drills com menor média no recorte recente.
    Query params:
      ?last_trainings=8   (quantidade de treinos recentes considerados)
      ?top=3              (quantos drills retornar)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        athlete = get_my_athlete_or_404(request.user)
        if not athlete:
            return Response({"detail": "Usuário não vinculado a atleta."}, status=404)

        last_trainings = int(request.query_params.get("last_trainings", "8"))
        top = int(request.query_params.get("top", "3"))

        # Pega IDs dos últimos N treinos em que o atleta participou
        training_ids = list(
            Attendance.objects
            .filter(athlete=athlete, status__in=["PRESENT", "LATE"])
            .order_by("-training__date", "-training__id")
            .values_list("training_id", flat=True)[:last_trainings]
        )

        if not training_ids:
            return Response({"items": []})

        # Calcula média por drill_name no recorte
        # (drill_name = name_override OU drill.name)
        qs = (
            DrillScore.objects
            .filter(
                athlete=athlete,
                training_drill__training_id__in=training_ids
            )
            .select_related("training_drill", "training_drill__drill")
        )

        # Normaliza o "nome do drill"
        # Se for de catálogo: usa training_drill__drill__name
        # Se for override: usa training_drill__name_override
        # Vamos agrupar via duas queries e unir (simples e robusto).
        catalog_group = (
            qs.filter(training_drill__drill__isnull=False)
            .values(drill_name=F("training_drill__drill__name"))
            .annotate(avg_score=Avg("score"))
        )

        override_group = (
            qs.filter(training_drill__drill__isnull=True, training_drill__name_override__isnull=False)
            .values(drill_name=F("training_drill__name_override"))
            .annotate(avg_score=Avg("score"))
        )

        merged = list(catalog_group) + list(override_group)

        # Ordena por menor média (pior) e retorna top N
        merged_sorted = sorted(merged, key=lambda x: (x["avg_score"] is None, x["avg_score"]))[:top]

        # Arredonda e inclui um "hint" de melhoria com base no último comentário daquele drill
        items = []
        for item in merged_sorted:
            drill_name = item["drill_name"]
            avg_score = float(item["avg_score"]) if item["avg_score"] is not None else None

            last_comment = (
                qs.filter(
                    training_drill__drill__name=drill_name
                ).order_by("-training_drill__training__date", "-id").values_list("comment", flat=True).first()
            )
            if not last_comment:
                last_comment = (
                    qs.filter(
                        training_drill__name_override__iexact=drill_name
                    ).order_by("-training_drill__training__date", "-id").values_list("comment", flat=True).first()
                )

            items.append({
                "drill_name": drill_name,
                "average_score": round(avg_score, 2) if avg_score is not None else None,
                "last_comment": last_comment,
            })

        return Response({"items": items, "scope_trainings": len(training_ids)})