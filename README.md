# Mamutes F.A. — Plataforma de Gestão de Flag Football

Plataforma para gestão técnica do time: atletas, treinos, presença, drills, notas, rankings, dashboards, relatórios e playbook de jogadas.

## Stack
- Backend: Django + Django REST Framework + SimpleJWT + SQLite
- Frontend: Vue 3 + Vuetify 4 + Vite + Pinia + Vue Router
- Gráficos: Chart.js (`vue-chartjs`)
- Upload de mídia: Pillow (fotos de atletas e imagens de jogadas)
- Relatórios: PDF/CSV (ReportLab)

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
  - listagem em cards (layout estilo “FC/OVR”) + métricas vindas da API
    - **OVR**: número grande no topo do card (0–100) derivado da nota do atleta: `OVR = round(rating * 10)`
      - `rating` vem da API (média ponderada de drills) e é limitado de 0 a 10
      - quando `rating` é 0, o card pode mostrar `OVR = --` (sem avaliação ainda)
    - **Cores do card por nota** (faixas do `rating`):
      - 0–6: cinza (crítico)
      - 7: vermelho (bom)
      - 8–9: verde claro (muito bom)
      - 10: dourado (excelente)
    - **Número da camisa**: usa o campo `jersey_number` e aparece no badge (círculo) do card quando existir
    - **Atributos (derivados)** exibidos abaixo do nome (placeholder visual, calculado por `rating` + `current_position`):
      - `VEL` (velocidade), `PAS` (passe), `REC` (recepção), `BLO` (bloqueio), `COB` (cobertura), `FOR` (força)
    - Foto preenche o frame (cover) e o nome tem efeito de “faixa/badge” (melhor legibilidade no light/dark)
  - métricas agregadas (`/api/athletes/stats/`) e `rating` por atleta
  - upload de foto com compressão automática no backend (Pillow) ao salvar o atleta
  - Regras de usuário (login) no cadastro de atleta:
    - no cadastro de atleta novo: é possível apenas **criar** um novo usuário (não lista/seleciona usuários existentes)
    - ao editar atleta: não é possível criar/vincular/alterar usuário
- Catálogo de drills: CRUD básico

- Combine: catálogo de testes, eventos e resultados
- Playbook: designer de jogadas (jogadores + rotas + tags) + CRUD

### Player
- Dashboard do player
- Meu Perfil (com preview card e edição)
- Atualização via `PATCH /api/athletes/me/` (inclui foto)

### Avisos
- Tela `Avisos` compartilhada (PLAYER/COACH/ADMIN)
- `COACH/ADMIN`: publicar (título obrigatório), fixar (`pinned`), editar e remover
- `PLAYER`: visualizar, curtir e comentar
- Push (PWA): botão **Notificar** usa Web Push (subscribe/unsubscribe) quando o servidor está configurado com VAPID

### Cofrinho
- Cofrinho global: `COACH/ADMIN` cria metas e todos os `PLAYER` conseguem ver
- Movimentações (depósito/retirada) apenas `COACH/ADMIN`; `PLAYER` é somente leitura

### UI/UX
- Layout com `NavigationDrawer` em modo `rail` (compacto) + header com perfil e toggle
- Drawer usa a foto real do atleta (quando existir), com fallback para avatar por iniciais
- Padrão visual: headers “sticky” com blur + cards `tonal` arredondados
- Toggle de tema (claro/escuro) com persistência (`localStorage`) via API do Vuetify `theme.change(...)`
- Botão PWA **Instalar** aparece quando o navegador disponibiliza o prompt e some após instalar/usar o prompt (persistido)
- Loading padrão com `%` (determinate): ciclo de ~5s e continua em loop enquanto a API não finalizar
  - composable: `frontend/src/composables/useProgressCircular.ts`

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
- Em `DJANGO_DEBUG=1` (default), mídia é servida via Django (`/media/...`).
- A pasta `media/` não é versionada (ver `.gitignore`).

Variáveis de ambiente (opcional):
- `DJANGO_DEBUG=1` ou `DJANGO_DEBUG=0`
- `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com`

#### Seed de dados (dev/demo)
Cria atletas (com foto), catálogo de drills, treinos, presença e notas. Opcionalmente, também semeia dados do Combine.

Dica (Windows): se você não ativou o venv, rode com `venv/Scripts/python.exe manage.py seed_random_data`.

```bash
# básico
python manage.py seed_random_data

# com reset + seed fixo
python manage.py seed_random_data --reset --seed 123

# parâmetros principais
python manage.py seed_random_data --athletes 30 --trainings 12 --catalog 20 --drills-min 6 --drills-max 10

# inclui combine (se o app existir)
python manage.py seed_random_data --with-combine
```

Parâmetros úteis:
- `--reset`: apaga dados de atletas/treinos (e combine se `--with-combine`) antes de semear
- `--seed`: semente para resultados determinísticos
- `--score-missing-rate`: chance de não gerar nota (0-1)

### Frontend (Vue)
Dev server em: `http://localhost:3000`

```bash
cd frontend

# escolha um
npm install
npm run dev

# ou
pnpm install
pnpm dev
```

Config de API do frontend:
- Está em `frontend/src/api/http.ts` (`resolveApiBaseUrl()`).
- Override (opcional): `VITE_API_BASE_URL` (ex: `http://127.0.0.1:8000` ou `http://127.0.0.1:8000/api`).
- Sem override: se o frontend estiver em uma porta diferente de `8000`, assume backend em `:8000`; caso contrário usa mesma origem.
- O axios usa `baseURL` em `/api` e remove automaticamente prefixos `api/` e `/api/` nas chamadas.

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

### Dashboard (player)
- `GET /api/dashboard/my/latest-training/`
- `GET /api/dashboard/my/drill-trends/`
- `GET /api/dashboard/my/improvements/`

### Notices (Avisos)
- `GET/POST /api/notices/` (POST: admin/coach)
- `GET/PATCH/DELETE /api/notices/{id}/` (PATCH/DELETE: admin/coach)
- `POST /api/notices/{id}/like/`
- `GET/POST /api/notices/{id}/comments/`

Push (PWA):
- `GET /api/notices/push/public-key/`
- `GET /api/notices/push/subscriptions/`
- `POST /api/notices/push/subscribe/`
- `POST /api/notices/push/unsubscribe/`

Config (backend, opcional):
- `WEBPUSH_VAPID_PUBLIC_KEY`
- `WEBPUSH_VAPID_PRIVATE_KEY` (PEM ou caminho para arquivo PEM)
- `WEBPUSH_VAPID_SUBJECT` (ex: `mailto:admin@mamutes.local`)

Gerar VAPID keys (opcional): `python manage.py generate_vapid_keys` (requer `py-vapid` e `cryptography`).

### Cashbox (Cofrinho)
- `GET/POST /api/cashbox/goals/` (POST: admin/coach)
- `GET/PATCH/DELETE /api/cashbox/goals/{id}/` (PATCH/DELETE: admin/coach)
- `GET/POST /api/cashbox/goals/{id}/transactions/` (POST: admin/coach)

### Combine
- `GET/POST /api/combine/tests/`
- `GET/POST /api/combine/events/`
- `GET/POST /api/combine/results/`

### Playbook
- `GET/POST /api/playbook/plays/`
- `GET/PATCH/DELETE /api/playbook/plays/{id}/`
- `POST /api/playbook/plays/{id}/clone/` (admin/coach)

Recursos (frontend):
- Designer (canvas) para posicionar jogadores e desenhar rotas
- Campo "Lado": `Ataque` / `Defesa` (`category`)
- `formation` e `play_type` são textos livres (cadastra na hora)
- Cards com preview (SVG), botão **Ver** (somente leitura) e **Duplicar** (coach/admin)
- Player acessa Playbook em modo `readOnly` (sem editar/duplicar/remover)

Rotas (frontend):
- Coach/Admin: `/coach/playbook`
- Player (somente leitura): `/player/playbook`

Permissões (API):
- `GET` (list/detail): qualquer usuário autenticado
- `POST/PATCH/DELETE/clone`: apenas `ADMIN` e `COACH`

Schema (Play):
- `name`: string
- `description`: string | null
- `category`: "Ataque" | "Defesa" | null
- `formation`: string (livre)
- `play_type`: string (livre)
- `tags`: string[]
- `players`: array de `{ id, x, y, role?, team?, label? }`
- `routes`: array de `{ player_id, points: [{x,y}], type?, color? }`

Observações:
- Campos antigos de imagem ainda existem (legado): `image` e `image_url`. O fluxo principal agora é via designer.

Upload de imagem:
- Envie multipart com o campo `image`
- Para remover a imagem: `PATCH` com `clear_image=true`

## Branding do PDF
Config em `core/settings.py`:
- `BRAND_NAME`
- `BRAND_LOGO_PATH` (ex: `media/brand/logo.png`)

## Licença
MIT — veja `LICENSE`.
