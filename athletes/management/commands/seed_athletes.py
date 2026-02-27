from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from athletes.models import Athlete


@dataclass(frozen=True)
class NameParts:
    first: str
    last: str


FIRST_NAMES = [
    "João",
    "Pedro",
    "Lucas",
    "Mateus",
    "Gabriel",
    "Rafael",
    "Bruno",
    "Gustavo",
    "Felipe",
    "Thiago",
    "Diego",
    "Henrique",
    "Caio",
    "Igor",
    "Vitor",
    "Daniel",
    "André",
    "Leonardo",
    "Marcos",
    "Eduardo",
]

LAST_NAMES = [
    "Silva",
    "Santos",
    "Oliveira",
    "Souza",
    "Lima",
    "Pereira",
    "Ferreira",
    "Almeida",
    "Costa",
    "Rodrigues",
    "Martins",
    "Araújo",
    "Ribeiro",
    "Carvalho",
    "Gomes",
    "Barbosa",
    "Melo",
    "Cardoso",
    "Teixeira",
    "Correia",
]

CITIES = [
    "São Paulo",
    "Campinas",
    "Rio de Janeiro",
    "Niterói",
    "Belo Horizonte",
    "Contagem",
    "Curitiba",
    "Londrina",
    "Porto Alegre",
    "Caxias do Sul",
    "Florianópolis",
    "Joinville",
    "Brasília",
    "Goiânia",
    "Salvador",
    "Fortaleza",
    "Recife",
    "Natal",
]


def _rand_decimal(low: float, high: float, places: int) -> Decimal:
    value = round(random.uniform(low, high), places)
    return Decimal(str(value))


class Command(BaseCommand):
    help = "Cria atletas fictícios para base de teste."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=20, help="Quantidade de atletas a criar (default: 20)")
        parser.add_argument(
            "--seed",
            type=int,
            default=20260227,
            help="Seed do gerador aleatório para resultados reproduzíveis (default: 20260227)",
        )
        parser.add_argument(
            "--prefix",
            type=str,
            default="Atleta",
            help="Prefixo opcional para nomes (default: Atleta)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count: int = max(1, int(options["count"]))
        seed: int = int(options["seed"])
        prefix: str = str(options["prefix"]).strip() or "Atleta"

        random.seed(seed)

        existing_names = set(Athlete.objects.values_list("name", flat=True))
        used_jerseys = set(
            int(x)
            for x in Athlete.objects.exclude(jersey_number__isnull=True).values_list("jersey_number", flat=True)
        )

        positions = [p[0] for p in Athlete.Position.choices]

        created = 0
        attempts = 0
        max_attempts = count * 20

        while created < count and attempts < max_attempts:
            attempts += 1

            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            suffix = random.randint(1, 999)
            name = f"{prefix} {first} {last} {suffix:03d}"
            if name in existing_names:
                continue

            # Jersey 1..99, try to keep unique
            jersey = None
            for _ in range(40):
                candidate = random.randint(1, 99)
                if candidate not in used_jerseys:
                    jersey = candidate
                    break
            if jersey is None:
                jersey = random.randint(1, 99)

            # birth_date: 16..35 years old
            year = random.randint(date.today().year - 35, date.today().year - 16)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            birth_date = date(year, month, day)

            Athlete.objects.create(
                name=name,
                jersey_number=jersey,
                birth_date=birth_date,
                birth_city=random.choice(CITIES),
                height_m=_rand_decimal(1.60, 1.98, 2),
                weight_kg=_rand_decimal(60.0, 120.0, 2),
                current_position=random.choice(positions),
                desired_position=random.choice(positions),
                career_notes="Atleta fictício gerado para testes.",
                is_active=True,
            )

            existing_names.add(name)
            used_jerseys.add(int(jersey))
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Criados {created} atletas fictícios."))
        if created < count:
            self.stdout.write(
                self.style.WARNING(
                    f"Apenas {created}/{count} criados (tentativas={attempts}). Rode novamente com outro --seed."
                )
            )
