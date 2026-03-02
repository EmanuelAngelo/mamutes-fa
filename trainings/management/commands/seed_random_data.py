from __future__ import annotations

import random
import string
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from io import BytesIO
from uuid import uuid4

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from athletes.models import Athlete
from trainings.models import Attendance, DrillCatalog, DrillScore, TrainingDrill, TrainingSession

try:
    from combine.models import AssessmentEvent, AssessmentResult, TestType

    HAS_COMBINE = True
except Exception:
    HAS_COMBINE = False

try:
    from PIL import Image, ImageDraw, ImageFont

    HAS_PIL = True
except Exception:
    HAS_PIL = False


@dataclass(frozen=True)
class SeedConfig:
    athletes: int
    trainings: int
    drills_catalog: int
    drills_per_training_min: int
    drills_per_training_max: int
    score_missing_rate: float
    seed: int | None
    reset: bool
    with_combine: bool


FOOTBALL_DRILLS = [
    # Offense
    ("Route Tree", "WR", "Trabalho de rotas: slant, out, comeback, go, post, corner."),
    ("Catching Gauntlet", "WR", "Sequência rápida de recepções em diferentes ângulos."),
    ("QB Footwork Drops", "QB", "Drops 3/5/7 passos + base e alinhamento."),
    ("Quick Game Timing", "QB", "Ritmo e timing do quick game com alvos curtos."),
    ("Pass Pro Sets", "OL", "Postura, kick slide e ângulos de proteção."),
    ("Run Fit - Inside Zone", "OL", "Bloqueios e combos do inside zone."),
    ("RB Read & Cut", "RB", "Leitura do gap e corte com baixa altura do quadril."),
    ("Ball Security", "RB", "Segurança de bola: high and tight, trocas e contatos."),
    # Defense
    ("Tackling Form", "DEF", "Ângulo, alavanca, wrap and drive."),
    ("Pursuit Angles", "DEF", "Ângulos de perseguição e contenção."),
    ("DB Backpedal & Break", "DB", "Backpedal, plant & drive, ângulos de quebra."),
    ("Press Technique", "DB", "Jam, mãos, quadril e espelhamento em press."),
    ("Coverage Drops", "LB", "Drops em zona (hook/curl/flat) e leitura do QB."),
    ("DL Get-Off", "DL", "Explosão na saída e hand fighting básico."),
    ("Blitz Pickup", "OFF", "Identificação de blitz e ajustes de proteção."),
    # Special teams / conditioning
    ("Kickoff Coverage Lanes", "ST", "Disciplina de lanes e contain."),
    ("Punt Return Ball Skills", "ST", "Leitura de bola e segurança na recepção."),
    ("Gassers", "COND", "Condicionamento: sprints de ida e volta (gassers)."),
    ("Pro Agility (5-10-5)", "COND", "Mudança de direção e aceleração curta."),
]

LOCATIONS = [
    "Campo Principal",
    "Campo Auxiliar",
    "Arena Municipal",
    "Quadra Coberta",
]

NOTES = [
    "Foco em técnica e ritmo.",
    "Treino leve pós-jogo.",
    "Instalação de conceitos novos.",
    "Trabalho de base e fundamentos.",
]

FIRST_NAMES = [
    "João",
    "Pedro",
    "Miguel",
    "Arthur",
    "Lucas",
    "Gabriel",
    "Matheus",
    "Guilherme",
    "Rafael",
    "Bruno",
    "Felipe",
    "Diego",
    "André",
    "Henrique",
    "Caio",
    "Thiago",
    "Leonardo",
    "Marcelo",
    "Vitor",
    "Daniel",
]

LAST_NAMES = [
    "Silva",
    "Santos",
    "Oliveira",
    "Souza",
    "Pereira",
    "Costa",
    "Ferreira",
    "Rodrigues",
    "Almeida",
    "Nascimento",
    "Lima",
    "Araujo",
    "Ribeiro",
    "Carvalho",
    "Gomes",
    "Martins",
]


def _rand_name(rng: random.Random) -> str:
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def _rand_jersey(rng: random.Random, used: set[int]) -> int:
    for _ in range(200):
        n = rng.randint(1, 99)
        if n not in used:
            used.add(n)
            return n
    n = rng.randint(1, 99)
    used.add(n)
    return n


def _rand_position(rng: random.Random) -> str:
    return rng.choice([p[0] for p in Athlete.Position.choices])


def _dec(val: float | int, places: int = 2) -> Decimal:
    q = Decimal("1").scaleb(-places)
    return Decimal(str(val)).quantize(q)


def _score_decimal(rng: random.Random, max_score: int) -> Decimal:
    raw = rng.uniform(max(0.0, max_score - 4.5), float(max_score))
    return Decimal(str(round(raw, 1))).quantize(Decimal("0.1"))


def _maybe_comment(rng: random.Random) -> str | None:
    if rng.random() < 0.65:
        return None
    return rng.choice(
        [
            "Boa execução.",
            "Precisa ajustar a base.",
            "Ótimo tempo de reação.",
            "Errou o ângulo.",
            "Melhorar mãos/pegada.",
            "Fadiga no final.",
        ]
    )


def _image_bytes(name: str, jersey: int, rng: random.Random) -> tuple[bytes, str]:
    if not HAS_PIL:
        raise RuntimeError("Pillow não disponível para gerar imagens.")

    size = 384
    bg = (rng.randint(20, 220), rng.randint(20, 220), rng.randint(20, 220))
    fg = (255, 255, 255)

    im = Image.new("RGB", (size, size), bg)
    draw = ImageDraw.Draw(im)

    initials = "".join([p[0] for p in name.split()[:2] if p]).upper()
    text = f"{initials}\n#{jersey}"

    # Fonte padrão (evita dependências externas)
    font = ImageFont.load_default()

    # Centralizar multiline de forma simples
    lines = text.split("\n")
    line_h = 18
    total_h = line_h * len(lines)
    y = (size - total_h) // 2

    for line in lines:
        w = draw.textlength(line, font=font)
        x = (size - int(w)) // 2
        draw.text((x, y), line, fill=fg, font=font)
        y += line_h

    # Borda
    draw.rectangle((6, 6, size - 6, size - 6), outline=(0, 0, 0), width=3)

    buf = BytesIO()
    im.save(buf, format="JPEG", quality=88)
    return buf.getvalue(), "jpg"


class Command(BaseCommand):
    help = "Cria dados aleatórios (atletas, treinos, drills, presença e avaliações) para desenvolvimento/demo."

    def add_arguments(self, parser):
        parser.add_argument("--athletes", type=int, default=24)
        parser.add_argument("--trainings", type=int, default=10)
        parser.add_argument("--catalog", type=int, default=18)
        parser.add_argument("--drills-min", type=int, default=6)
        parser.add_argument("--drills-max", type=int, default=10)
        parser.add_argument("--seed", type=int, default=None)
        parser.add_argument("--reset", action="store_true", help="Apaga dados de atletas/treinos/combine antes de semear.")
        parser.add_argument(
            "--with-combine",
            action="store_true",
            help="Também cria dados aleatórios de combine (TestType/Event/Results).",
        )
        parser.add_argument(
            "--score-missing-rate",
            type=float,
            default=0.08,
            help="Probabilidade de NÃO gerar nota para um atleta em um drill (0-1).",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        config = SeedConfig(
            athletes=max(1, int(opts["athletes"])),
            trainings=max(1, int(opts["trainings"])),
            drills_catalog=max(1, int(opts["catalog"])),
            drills_per_training_min=max(1, int(opts["drills_min"])),
            drills_per_training_max=max(1, int(opts["drills_max"])),
            score_missing_rate=float(opts["score_missing_rate"]),
            seed=opts.get("seed"),
            reset=bool(opts.get("reset")),
            with_combine=bool(opts.get("with_combine")),
        )

        if config.drills_per_training_min > config.drills_per_training_max:
            raise ValueError("--drills-min não pode ser maior que --drills-max")

        rng = random.Random(config.seed)

        if config.reset:
            self._reset_data(config)

        athletes = self._seed_athletes(rng, config)
        catalog = self._seed_catalog(rng, config)
        trainings = self._seed_trainings(rng, config)

        self._seed_training_content(rng, config, trainings, athletes, catalog)

        if config.with_combine and HAS_COMBINE:
            self._seed_combine(rng, athletes)

        self.stdout.write(self.style.SUCCESS("Seed concluído."))

    def _reset_data(self, config: SeedConfig):
        DrillScore.objects.all().delete()
        Attendance.objects.all().delete()
        TrainingDrill.objects.all().delete()
        TrainingSession.objects.all().delete()
        DrillCatalog.objects.all().delete()

        if config.with_combine and HAS_COMBINE:
            AssessmentResult.objects.all().delete()
            AssessmentEvent.objects.all().delete()
            TestType.objects.all().delete()

        Athlete.objects.all().delete()

    def _seed_athletes(self, rng: random.Random, config: SeedConfig):
        used_numbers: set[int] = set()
        athletes: list[Athlete] = []

        for _ in range(config.athletes):
            name = _rand_name(rng)
            jersey = _rand_jersey(rng, used_numbers)

            a = Athlete(
                name=name,
                jersey_number=jersey,
                birth_city=rng.choice(["São Paulo", "Campinas", "Santos", "Guarulhos", "Sorocaba", "Osasco"]),
                birth_date=date.today() - timedelta(days=rng.randint(16 * 365, 34 * 365)),
                height_m=_dec(rng.uniform(1.62, 1.98), places=2),
                weight_kg=_dec(rng.uniform(65, 125), places=2),
                current_position=_rand_position(rng),
                desired_position=_rand_position(rng),
                career_notes=rng.choice([None, "Rookie", "Veterano", "Foco em fundamentos", "Voltando de lesão"]) or "",
                is_active=rng.random() > 0.08,
            )

            if HAS_PIL:
                img, ext = _image_bytes(name, jersey, rng)
                filename = f"seed_{uuid4().hex}.{ext}"
                a.photo.save(filename, ContentFile(img), save=False)

            a.save()
            athletes.append(a)

        return athletes

    def _seed_catalog(self, rng: random.Random, config: SeedConfig):
        base = FOOTBALL_DRILLS[:]
        rng.shuffle(base)

        # Garante quantidade pedida (com nomes extras se necessário)
        while len(base) < config.drills_catalog:
            suffix = "".join(rng.choices(string.ascii_uppercase, k=3))
            base.append((f"Fundamentals {suffix}", "GEN", "Fundamentos gerais."))

        created: list[DrillCatalog] = []
        for name, category, desc in base[: config.drills_catalog]:
            obj, _ = DrillCatalog.objects.get_or_create(
                name=name,
                defaults={"category": category, "description": desc},
            )
            created.append(obj)
        return created

    def _seed_trainings(self, rng: random.Random, config: SeedConfig):
        trainings: list[TrainingSession] = []
        today = date.today()

        for i in range(config.trainings):
            d = today - timedelta(days=rng.randint(1, 90))
            # horários típicos
            st = time(hour=rng.choice([18, 19, 20]), minute=rng.choice([0, 10, 20, 30, 40, 50]))

            t = TrainingSession.objects.create(
                date=d,
                start_time=st,
                location=rng.choice(LOCATIONS),
                notes=rng.choice(NOTES),
            )
            trainings.append(t)

        trainings.sort(key=lambda x: x.date)
        return trainings

    def _seed_training_content(
        self,
        rng: random.Random,
        config: SeedConfig,
        trainings: list[TrainingSession],
        athletes: list[Athlete],
        catalog: list[DrillCatalog],
    ):
        active_athletes = [a for a in athletes if a.is_active]
        if not active_athletes:
            active_athletes = athletes

        for t in trainings:
            drills_count = rng.randint(config.drills_per_training_min, config.drills_per_training_max)
            drills = rng.sample(catalog, k=min(drills_count, len(catalog)))

            training_drills: list[TrainingDrill] = []
            order = 1
            for dc in drills:
                td = TrainingDrill.objects.create(
                    training=t,
                    drill=dc,
                    name_override=None,
                    order=order,
                    description=dc.description,
                    max_score=10,
                    weight=_dec(rng.uniform(0.5, 2.0), places=2),
                )
                training_drills.append(td)
                order += 1

            # presença: maioria presente
            for a in active_athletes:
                r = rng.random()
                if r < 0.82:
                    status = Attendance.Status.PRESENT
                elif r < 0.90:
                    status = Attendance.Status.LATE
                elif r < 0.96:
                    status = Attendance.Status.JUSTIFIED
                else:
                    status = Attendance.Status.ABSENT

                Attendance.objects.get_or_create(
                    training=t,
                    athlete=a,
                    defaults={"status": status, "checkin_time": None},
                )

            # notas: gera para todos exceto faltantes (e um pouco de missing)
            absent_ids = set(
                Attendance.objects.filter(training=t, status=Attendance.Status.ABSENT).values_list(
                    "athlete_id", flat=True
                )
            )

            for td in training_drills:
                for a in active_athletes:
                    if a.id in absent_ids:
                        continue
                    if rng.random() < config.score_missing_rate:
                        continue

                    DrillScore.objects.get_or_create(
                        training_drill=td,
                        athlete=a,
                        defaults={
                            "score": _score_decimal(rng, td.max_score),
                            "comment": _maybe_comment(rng),
                            "rated_by": None,
                        },
                    )

    def _seed_combine(self, rng: random.Random, athletes: list[Athlete]):
        # Tipos comuns no futebol americano
        test_specs = [
            ("40Y", "40-Yard Dash", "s", True),
            ("VJ", "Vertical Jump", "cm", False),
            ("BJ", "Broad Jump", "cm", False),
            ("BP", "Bench Press Reps", "reps", False),
            ("SH", "Shuttle (20y)", "s", True),
            ("3C", "3-Cone Drill", "s", True),
        ]

        types: list[TestType] = []
        for code, name, unit, lower_is_better in test_specs:
            tt, _ = TestType.objects.get_or_create(
                code=code,
                defaults={"name": name, "unit": unit, "lower_is_better": lower_is_better},
            )
            types.append(tt)

        season = date.today().year
        ev, _ = AssessmentEvent.objects.get_or_create(
            name=f"Combine Demo {season}",
            defaults={"season_year": season, "date": date.today() - timedelta(days=rng.randint(1, 60))},
        )

        for a in athletes:
            for tt in types:
                if tt.code in ("40Y", "SH", "3C"):
                    value = _dec(rng.uniform(4.6, 6.2), places=2)
                elif tt.code in ("VJ",):
                    value = _dec(rng.uniform(45, 90), places=2)
                elif tt.code in ("BJ",):
                    value = _dec(rng.uniform(180, 330), places=2)
                elif tt.code in ("BP",):
                    value = _dec(rng.randint(5, 30), places=2)
                else:
                    value = _dec(rng.uniform(1, 100), places=2)

                AssessmentResult.objects.get_or_create(
                    event=ev,
                    athlete=a,
                    test_type=tt,
                    defaults={"value": value, "notes": None},
                )
