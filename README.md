# 🏈 Mamutes F.A. -- Plataforma de Gestão de Flag Football

Sistema completo para gestão de time de Flag Football, desenvolvido com:

-   **Backend:** Django + Django REST Framework
-   **Frontend:** Vue 3 + Vuetify 3 + Tailwind
-   **Autenticação:** JWT (SimpleJWT)
-   **Gráficos:** Chart.js
-   **Exportação:** PDF Premium (ReportLab)

------------------------------------------------------------------------

# 📌 Visão Geral

A plataforma permite:

-   Cadastro completo de atletas
-   Controle de presença em treinos
-   Cadastro de drills por treino
-   Lançamento de notas (0--10) por drill
-   Cálculo de média ponderada por treino
-   Ranking com desempate automático
-   Ranking por posição (QB, WR, DB, etc.)
-   Dashboard do jogador com gráficos de evolução
-   Dashboard do coach com matriz de notas
-   Exportação premium em PDF com:
    -   Capa personalizada
    -   Resumo executivo
    -   Top 3 geral e por posição
    -   Gráfico de desempenho
    -   Presença
    -   Ranking completo
    -   Notas detalhadas por drill

------------------------------------------------------------------------

# 🧠 Arquitetura

## Backend (Django)

Apps principais:

-   accounts
-   athletes
-   trainings
-   combine
-   dashboard

Principais recursos:

-   JWT Authentication
-   Permissões por role (ADMIN, COACH, PLAYER)
-   Média ponderada por peso do drill
-   Ranking com critério de desempate:
    1.  Maior média ponderada
    2.  Maior número de drills avaliados
    3.  Maior soma ponderada de pontos
    4.  Ordem alfabética

------------------------------------------------------------------------

## Frontend (Vuetify 3)

Estrutura:

-   Layout com Drawer + AppBar
-   Guards por Role
-   Dashboard Player
-   Dashboard Coach
-   Gráficos com Chart.js
-   Matriz de notas interativa
-   Exportação PDF via backend

------------------------------------------------------------------------

# 🚀 Como Rodar o Projeto

## 🔹 Backend

``` bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Servidor padrão:

    http://127.0.0.1:8000

------------------------------------------------------------------------

## 🔹 Frontend

``` bash
cd frontend
npm install
npm run dev
```

Frontend padrão:

    http://localhost:5173

------------------------------------------------------------------------

# 🔐 Roles

  Role     Acesso
  -------- ----------------------------------------
  ADMIN    Controle total
  COACH    Gerencia treinos, atletas e relatórios
  PLAYER   Visualiza próprio desempenho

------------------------------------------------------------------------

# 📊 Funcionalidades Avançadas

## Média Ponderada

Cada drill pode possuir peso diferente.

Fórmula:

Média = Σ(score × weight) / Σ(weight)

------------------------------------------------------------------------

## Ranking por Posição

Exemplo: - WR - QB - DB - RB - CB - S - C - R

------------------------------------------------------------------------

## Relatório PDF Premium

Inclui:

-   Capa com logo do time
-   Sumário executivo
-   Gráfico Top 10
-   Ranking completo
-   Ranking por posição
-   Presença
-   Notas detalhadas por drill
-   Paginação automática

------------------------------------------------------------------------

# 📦 Estrutura do Projeto

    mamutes_fa/
    │
    ├── backend (Django)
    │
    └── frontend (Vue + Vuetify)

------------------------------------------------------------------------

# 🎯 Próximas Evoluções Possíveis

-   Comparação entre treinos
-   Evolução por temporada
-   MVP do treino automático
-   Most Improved Player
-   Exportação Excel
-   Modo mobile otimizado
-   Upload de vídeo por drill

------------------------------------------------------------------------

# 🏆 Objetivo do Projeto

Criar uma plataforma profissional de gestão técnica para time de Flag
Football, permitindo análise de desempenho, evolução individual e tomada
de decisão baseada em dados.

------------------------------------------------------------------------

Desenvolvido para o time **Mamutes F.A.**
