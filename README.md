# Mamutes F.A. — Plataforma de Gestão de Flag Football

Sistema para gestão técnica do time (treinos, atletas, presença, drills, notas, rankings e relatórios).

**Stack atual**
- Backend: Django 6 + Django REST Framework + SimpleJWT + SQLite
- Frontend: Vue 3 + Vuetify 4 + Vite + Pinia + Vue Router
- Relatórios: PDF via ReportLab
- Gráficos: Chart.js

## Funcionalidades (atual)
- CRUD de atletas (campos alinhados ao model do Django)
- CRUD de treinos
- Tela de detalhe do treino (coach):
  - lista de presença (salva via endpoint bulk)
  - drills do treino (adiciona via endpoint bulk e remove via endpoint de drills)
  - avaliação individual (atleta + drill + nota + comentário)
  - dashboard do coach (ranking, médias, etc.)
  - exportação PDF do treino
- Coach Dashboard (home do coach):
  - gráficos de tendência (média do treino ao longo dos últimos treinos)
  - gráfico de médias por drill (último treino)

## Responsividade (mobile)
- `AppLayout` com padding responsivo e conteúdo em container `fluid`.
- Tabelas com rolagem horizontal (classe `.table-scroll`) para evitar overflow no mobile.
- Dialogs de criação/edição em fullscreen no mobile (ex.: atletas e treinos).

## UI (Login)
- A imagem de fundo (`Time_1.jpg`) aparece **apenas na tela de login**.
- Após login, a aplicação volta ao fundo padrão/escuro do Vuetify.

## Como rodar

### Backend (Django)
Servidor padrão: `http://127.0.0.1:8000`

```bash
cd /c/Users/u12512/Projetos/mamutes_fa

# (opcional) criar e ativar venv
python -m venv venv
source venv/Scripts/activate

# instalar deps (se o requirements.txt estiver preenchido)
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Observações:
- O projeto usa SQLite por padrão (`db.sqlite3`).
- Em dev, o CORS está liberado (`CORS_ALLOW_ALL_ORIGINS=True`).

### Frontend (Vue)
Servidor padrão: `http://localhost:3000`

O frontend lê a base da API por `VITE_API_BASE_URL` (arquivo `frontend/.env`).

```bash
cd /c/Users/u12512/Projetos/mamutes_fa/frontend
pnpm install
pnpm dev
```

## Autenticação e roles
Roles: `ADMIN`, `COACH`, `PLAYER`.

Endpoints de auth:
- `POST /api/accounts/login/` (JWT)
- `POST /api/accounts/refresh/`
- `GET /api/accounts/me/`

## Endpoints principais (API)

Atletas:
- `GET/POST /api/athletes/`
- `GET/PATCH/DELETE /api/athletes/{id}/`

Treinos:
- `GET/POST /api/trainings/`
- `GET/PATCH/DELETE /api/trainings/{id}/`

Catálogo de drills:
- `GET /api/trainings/catalog/`

Coach (treino):
- `GET /api/trainings/{id}/coach_dashboard/`
- `POST /api/trainings/{id}/attendance_bulk/` (lista de presença)
- `POST /api/trainings/{id}/drills_bulk/` (drills do treino)
- `POST /api/trainings/{id}/scores_bulk/` (salvar/atualizar nota + comentário por atleta/drill)
- `DELETE /api/trainings/drills/{training_drill_id}/` (remover drill do treino)
- `GET /api/trainings/{id}/export/pdf/`
- `GET /api/trainings/{id}/export/csv/`

Coach (dashboard):
- `GET /api/trainings/coach_overview/?limit=8` (dados para gráficos do Coach Dashboard)

## Branding do PDF
Config em `core/settings.py`:
- `BRAND_NAME`
- `BRAND_LOGO_PATH` (default: `media/brand/logo.png`)
