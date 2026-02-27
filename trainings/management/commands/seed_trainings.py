from __future__ import annotations

import random
from datetime import date, timedelta, time
from decimal import Decimal
from typing import Iterable

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from athletes.models import Athlete
from trainings.models import Attendance, DrillCatalog, DrillScore, TrainingDrill, TrainingSession


DRILL_LIBRARY: list[tuple[str, str, str]] = [
    ("Route Tree", "Recepção", "Execução de rotas e timing com o QB."),
    ("Release + Catch", "Recepção", "Saída da linha + recepção sob pressão."),
    ("1v1 Man Coverage", "Defesa", "Cobertura individual e contest do passe."),
    ("Zone Drops", "Defesa", "Leitura e queda em zona (hook/curl/flat)."),
    ("QB Accuracy", "QB", "Precisão em alvos curtos/médios/longos."),
    ("Snap + Exchange", "Center", "Troca e consistência do snap."),
    ("Hand-off Mechanics", "RB", "Mecânica de handoff e proteção da bola."),
    ("Pull Flags", "Defesa", "Técnica de flag pull e ângulo de abordagem."),
    ("Pursuit Angles", "Defesa", "Ângulos de perseguição e contenção."),
    ("Ball Skills", "Recepção", "Ataque à bola e controle em contato."),
    ("Footwork Ladder", "Atletismo", "Agilidade e coordenação de pés."),
    ("Conditioning", "Físico", "Resistência/condicionamento geral."),
    ("Red Zone Concepts", "Ofensiva", "Execução em espaço curto."),
    ("Blitz Pickup", "Ofensiva", "Reconhecer blitz e ajustar."),
    ("Blitz Timing", "Defesa", "Timing de blitz e contenção."),
    ("Open Field Tackling (Flag)", "Defesa", "Conter e finalizar o flag pull em campo aberto."),
    ("Two-Minute Drill", "Ofensiva", "Execução em ritmo acelerado."),
    ("Communication", "Time", "Comunicação pré-snap e ajustes."),
    ("Playbook Quiz", "Time", "Conhecimento do playbook e alinhamentos."),
    ("Special Situations", "Time", "Situações especiais e tomada de decisão."),
]

LOCATIONS = [
    "Campo Municipal",
    "Arena Treino",
    "CT Mamutes",
    "Quadra Central",
    "Campo do Parque",
]


def _rand_decimal(low: float, high: float, places: int = 1) -> Decimal:
    value = round(random.uniform(low, high), places)
    return Decimal(str(value))


def _chunks(items: list, size: int) -> Iterable[list]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


class Command(BaseCommand):
    help = "Cria drills, treinos, presença e pontuações fictícias para base de teste."

    def add_arguments(self, parser):
        parser.add_argument("--trainings", type=int, default=8, help="Qtd de treinos a criar (default: 8)")
        parser.add_argument("--drills", type=int, default=6, help="Qtd de drills por treino (default: 6)")
        parser.add_argument(
            "--score-fill",
            type=float,
            default=0.9,
            help="Probabilidade de gerar nota para (atleta presente x drill) (0..1; default: 0.9)",
        )
        parser.add_argument(
            "--attendance-rate",
            type=float,
            default=0.85,
            help="Probabilidade de um atleta estar PRESENT/LATE em um treino (0..1; default: 0.85)",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=20260227,
            help="Seed do gerador aleatório para resultados reproduzíveis (default: 20260227)",
        )
        parser.add_argument(
            "--created-by",
            type=str,
            default="",
            help="Username do usuário que será setado em TrainingSession.created_by e DrillScore.rated_by (opcional)",
        )
        parser.add_argument(
            "--catalog",
            type=int,
            default=20,
            help="Qtd de itens no catálogo de drills a garantir (default: 20)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        trainings_count = max(1, int(options["trainings"]))
        drills_per_training = max(1, int(options["drills"]))
        score_fill = float(options["score_fill"])
        attendance_rate = float(options["attendance_rate"])
        seed = int(options["seed"])
        created_by_username = str(options["created_by"]).strip()
        catalog_target = max(1, int(options["catalog"]))

        score_fill = max(0.0, min(score_fill, 1.0))
        attendance_rate = max(0.0, min(attendance_rate, 1.0))

        random.seed(seed)

        User = get_user_model()
        created_by = None
        if created_by_username:
            created_by = User.objects.filter(username=created_by_username).first()
            if not created_by:
                self.stdout.write(self.style.WARNING(f"Usuário '{created_by_username}' não encontrado; created_by ficará vazio."))

        athletes = list(Athlete.objects.all().order_by("id"))
        if not athletes:
            self.stdout.write(self.style.ERROR("Nenhum atleta encontrado. Rode primeiro: python manage.py seed_athletes --count 20"))
            return

        # -------------------------
        # 1) Garantir catálogo drills
        # -------------------------
        existing_catalog = list(DrillCatalog.objects.all().order_by("id"))
        if len(existing_catalog) < catalog_target:
            need = catalog_target - len(existing_catalog)
            lib = DRILL_LIBRARY[:]
            random.shuffle(lib)

            # cria itens novos (sem depender de nomes fixos)
            created_now = 0
            for name, category, desc in lib:
                if created_now >= need:
                    break
                obj, created = DrillCatalog.objects.get_or_create(
                    name=name,
                    defaults={"category": category, "description": desc},
                )
                if created:
                    created_now += 1

            # se ainda faltar, cria nomes genéricos
            i = 1
            while len(DrillCatalog.objects.all()) < catalog_target:
                generic_name = f"Drill Teste {i:02d}"
                DrillCatalog.objects.get_or_create(
                    name=generic_name,
                    defaults={
                        "category": "Teste",
                        "description": "Drill fictício gerado para testes.",
                    },
                )
                i += 1

        catalog = list(DrillCatalog.objects.all().order_by("name"))

        # -------------------------
        # 2) Criar treinos (datas únicas e aleatórias)
        # -------------------------
        today = date.today()
        created_trainings: list[TrainingSession] = []

        existing_dates = set(TrainingSession.objects.values_list("date", flat=True))
        picked_dates: list[date] = []
        picked_set: set[date] = set()

        # Gera datas aleatórias no passado recente e garante que não repete
        # (nem dentro da execução, nem com treinos já existentes no banco).
        days_back_max = max(60, trainings_count * 14)
        attempts = 0
        while len(picked_dates) < trainings_count:
            attempts += 1
            if attempts > 5000:
                days_back_max *= 2
                attempts = 0

            candidate = today - timedelta(days=random.randint(0, days_back_max))
            if candidate in existing_dates or candidate in picked_set:
                continue
            picked_set.add(candidate)
            picked_dates.append(candidate)

        picked_dates.sort()  # chronological

        for d in picked_dates:
            t = TrainingSession.objects.create(
                date=d,
                start_time=time(hour=20, minute=0),
                location=random.choice(LOCATIONS),
                notes="Treino fictício gerado para testes.",
                created_by=created_by,
            )
            created_trainings.append(t)

            # -------------------------
            # 3) Presença (Attendance)
            # -------------------------
            attendance_bulk: list[Attendance] = []
            for a in athletes:
                if random.random() <= attendance_rate:
                    status = "LATE" if random.random() < 0.08 else "PRESENT"
                else:
                    status = "JUSTIFIED" if random.random() < 0.25 else "ABSENT"

                attendance_bulk.append(
                    Attendance(
                        training=t,
                        athlete=a,
                        status=status,
                        checkin_time=
                            time(hour=20, minute=random.choice([0, 5, 10, 15, 20, 25, 30]))
                            if status in ("PRESENT", "LATE")
                            else None,
                    )
                )
            Attendance.objects.bulk_create(attendance_bulk, ignore_conflicts=True)

            # -------------------------
            # 4) Drills do treino
            # -------------------------
            chosen = random.sample(catalog, k=min(drills_per_training, len(catalog)))
            drills_created: list[TrainingDrill] = []
            for order, drill in enumerate(chosen, start=1):
                drills_created.append(
                    TrainingDrill(
                        training=t,
                        drill=drill,
                        name_override=None,
                        order=order,
                        description=drill.description,
                        max_score=10,
                        weight=_rand_decimal(0.5, 2.5, 2),
                    )
                )
            TrainingDrill.objects.bulk_create(drills_created)

            created_drills = list(TrainingDrill.objects.filter(training=t).order_by("order", "id"))

            # -------------------------
            # 5) Pontuações (DrillScore)
            # -------------------------
            present_ids = set(
                Attendance.objects.filter(training=t, status__in=["PRESENT", "LATE"]).values_list("athlete_id", flat=True)
            )

            score_bulk: list[DrillScore] = []
            for td in created_drills:
                for a in athletes:
                    if a.id not in present_ids:
                        continue
                    if random.random() > score_fill:
                        continue

                    score = _rand_decimal(0.0, 10.0, 1)
                    comment = None
                    if random.random() < 0.12:
                        comment = random.choice(
                            [
                                "Boa execução.",
                                "Precisa ajustar timing.",
                                "Melhorar técnica e consistência.",
                                "Ótima evolução.",
                                "Foco em detalhes.",
                            ]
                        )

                    score_bulk.append(
                        DrillScore(
                            training_drill=td,
                            athlete=a,
                            score=score,
                            comment=comment,
                            rated_by=created_by,
                        )
                    )

            for chunk in _chunks(score_bulk, 2000):
                DrillScore.objects.bulk_create(chunk, ignore_conflicts=True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed concluído: {len(catalog)} drills no catálogo, {len(created_trainings)} treinos criados, "
                f"com presença e pontuações."
            )
        )
