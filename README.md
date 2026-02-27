# Mamutes F.A. — Plataforma de Gestão de Flag Football

Plataforma para gestão técnica do time: atletas, treinos, presença, drills, notas, rankings, dashboards e relatórios.

## Stack
- Backend: Django 5 + Django REST Framework + SimpleJWT + SQLite
- Frontend: Vue 3 + Vuetify 4 + Vite + Pinia + Vue Router
- Gráficos: Chart.js (`vue-chartjs`)
- Relatórios: PDF/CSV (ReportLab + CSV)

## O que já existe (até agora)

### Auth e roles
- Roles: `ADMIN`, `COACH`, `PLAYER`
- Login JWT, refresh token, `me` e troca de senha no app

### Coach
- Dashboard (overview):
  - tendência da média ponderada do time nos últimos treinos
  - média por drill do último treino
  - insights de evolução entre os 2 últimos treinos (maior evolução e regressão)
  - insights do último treino (drill mais difícil e atleta mais consistente)
- Treinos:
  - CRUD de sessões de treino
  - detalhe do treino com presença, drills, matriz de notas e ranking (geral e por posição)
  - bulk endpoints para presença/drills/notas
  - exportação do treino em PDF e CSV
- Atletas:
  - CRUD de atletas com foto
  - listagem em cards (layout “FIFA-style”) + métricas vindas da API
  - métricas agregadas (`/api/athletes/stats/`) e `rating` por atleta
- Catálogo de drills: CRUD básico

### Player
- Dashboard do player
- Meu Perfil (com preview card e edição)
- Atualização via `PATCH /api/athletes/me/` (inclui foto)

### UI/UX
- Layout com `NavigationDrawer` em modo `rail` (compacto) + header com perfil e toggle
- Drawer usa a foto real do atleta (quando existir), com fallback para avatar por iniciais
- Padrão visual: headers “sticky” com blur + cards `tonal` arredondados

## Como rodar (dev)

### Backend (Django)
API em: `http://127.0.0.1:8000/api`

```bash
# na raiz do projeto
python -m venv venv
source venv/Scripts/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Notas:
- Banco padrão: `db.sqlite3`
- Em `DEBUG=True`, mídia é servida via Django (`/media/...`).

### Seed (dados fictícios para teste)

Para facilitar testes no frontend (coach/player) e validar rankings/analytics, existem comandos de seed.

Cria atletas fictícios (20 por padrão):

```bash
python manage.py seed_athletes --count 20
```

Cria catálogo de drills + treinos + presença + pontuações (com notas 0..10) — os treinos são gerados com **datas aleatórias e únicas**:

```bash
python manage.py seed_trainings --trainings 8 --drills 6
```

Opções úteis:
- Reproduzível: `--seed 123`
- Preencher `created_by`/`rated_by` (usa um username existente): `--created-by coach`
- Ajustar volume de notas/presença:
  - `--score-fill 0.95` (chance de gerar nota por atleta x drill)
  - `--attendance-rate 0.90` (chance do atleta estar PRESENT/LATE no treino)

### Frontend (Vue)
Dev server em: `http://localhost:3000`

```bash
cd frontend
npm install
npm run dev
```

Config de API do frontend:
- Hoje está em `frontend/src/api/http.ts` (const `API_BASE_URL`).
- O axios usa `baseURL = ${API_BASE_URL}/api` e remove automaticamente prefixos `/api/...` nas chamadas.

## Endpoints principais

### Accounts
- `POST /api/accounts/login/`
- `POST /api/accounts/refresh/`
- `GET /api/accounts/me/`
- `POST /api/accounts/change-password/`
- `GET/POST /api/accounts/users/` (admin/coach)

### Athletes
- `GET/POST /api/athletes/` (admin/coach)
- `GET/PATCH/DELETE /api/athletes/{id}/` (admin/coach)
- `GET /api/athletes/stats/` (admin/coach)
- `GET/PATCH /api/athletes/me/` (usuário autenticado vinculado ao atleta)

### Trainings
- `GET/POST /api/trainings/`
- `GET/PATCH/DELETE /api/trainings/{id}/`
- `GET /api/trainings/{id}/ranking/?position=WR` (admin/coach)
- `GET /api/trainings/{id}/coach_dashboard/` (admin/coach)

Bulk (admin/coach):
- `POST /api/trainings/{id}/attendance_bulk/`
- `POST /api/trainings/{id}/drills_bulk/`
- `POST /api/trainings/{id}/scores_bulk/`

Analytics/evolução (admin/coach):
- `GET /api/trainings/{id}/analytics/` (distribuição, desvio padrão, gaps, médias por posição/drill, drill mais difícil, atleta mais consistente)
- `GET /api/trainings/evolution/?limit=8&athlete_id=123` (tendência do time, tendência individual opcional e comparação entre os 2 últimos treinos)
- `GET /api/trainings/coach_overview/?limit=8` (overview legado: tendência + último treino)

Catálogo e recursos:
- `GET/POST /api/trainings/catalog/`
- `GET/POST /api/trainings/drills/`
- `GET/POST /api/trainings/scores/`

Export (admin/coach):
- `GET /api/trainings/{id}/export/pdf/`
- `GET /api/trainings/{id}/export/csv/`

## Branding do PDF
Config em `core/settings.py`:
- `BRAND_NAME`
- `BRAND_LOGO_PATH` (ex: `media/brand/logo.png`)

## Licença
MIT — veja `LICENSE`.
