<template>
  <div class="cofrinho-page">
    <header class="cofrinho-header">
      <v-container class="cofrinho-container">
        <div class="d-flex flex-wrap align-center justify-space-between ga-4 py-4">
          <div class="d-flex align-center ga-3">
            <div class="brand-icon">
              <v-icon size="22" color="white">mdi-piggy-bank</v-icon>
            </div>
            <div>
              <div class="text-subtitle-1 font-weight-bold">Meu Cofrinho</div>
              <div class="text-caption text-medium-emphasis">Economize para seus sonhos</div>
            </div>
          </div>

          <v-btn
            v-if="auth.isCoachOrAdmin"
            class="btn-new-goal"
            rounded="pill"
            :loading="creatingGoal"
            @click="openNewGoal"
          >
            <v-icon start size="18">mdi-plus</v-icon>
            <span class="d-none d-sm-inline">Nova Meta</span>
            <span class="d-inline d-sm-none">Nova</span>
          </v-btn>
        </div>
      </v-container>
    </header>

    <main>
      <v-container class="cofrinho-container py-6">
        <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
          {{ error }}
        </v-alert>

        <div v-if="loading" class="d-flex align-center justify-center py-16">
          <div class="spinner" />
        </div>

        <template v-else>
          <section v-if="goals.length === 0" class="empty">
            <div class="empty__circle">
              <v-icon size="56">mdi-piggy-bank</v-icon>
            </div>
            <div class="text-h6 font-weight-bold mt-5">Seu cofrinho está vazio</div>
            <div class="text-body-2 text-medium-emphasis mt-2" style="max-width: 420px">
              Crie sua primeira meta de economia e comece a guardar dinheiro para realizar seus sonhos!
            </div>

            <v-btn
              v-if="auth.isCoachOrAdmin"
              class="btn-new-goal mt-7"
              rounded="pill"
              @click="openNewGoal"
            >
              <v-icon start size="18">mdi-plus</v-icon>
              Criar primeira meta
            </v-btn>
          </section>

          <template v-else>
            <v-row density="comfortable" class="mb-6">
              <v-col cols="12" sm="6" lg="3">
                <v-card class="summary summary--violet" rounded="xl">
                  <v-card-text>
                    <v-icon class="summary__icon">mdi-piggy-bank</v-icon>
                    <div class="summary__label">TOTAL ECONOMIZADO</div>
                    <div class="summary__value">{{ formatBRL(totalSaved) }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" sm="6" lg="3">
                <v-card class="summary summary--blue" rounded="xl">
                  <v-card-text>
                    <v-icon class="summary__icon">mdi-target</v-icon>
                    <div class="summary__label">TOTAL DAS METAS</div>
                    <div class="summary__value">{{ formatBRL(totalTarget) }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" sm="6" lg="3">
                <v-card class="summary summary--amber" rounded="xl">
                  <v-card-text>
                    <v-icon class="summary__icon">mdi-trending-up</v-icon>
                    <div class="summary__label">METAS ATIVAS</div>
                    <div class="summary__value">{{ activeGoals.length }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" sm="6" lg="3">
                <v-card class="summary summary--green" rounded="xl">
                  <v-card-text>
                    <v-icon class="summary__icon">mdi-check-circle</v-icon>
                    <div class="summary__label">METAS CONCLUÍDAS</div>
                    <div class="summary__value">{{ completedGoals.length }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <section v-if="activeGoals.length" class="mb-8">
              <div class="text-subtitle-1 font-weight-bold mb-4">Metas Ativas</div>

              <TransitionGroup name="goal" tag="div" class="goals-grid">
                <div v-for="goal in activeGoals" :key="goal.id" class="goal-wrap">
                  <v-card
                    class="goal-card"
                    :class="`cat-${goal.category}`"
                    rounded="xl"
                    variant="elevated"
                    @click="auth.isCoachOrAdmin ? openAddMoney(goal) : null"
                  >
                    <div class="goal-card__topbar" :style="{ width: `${percent(goal)}%` }" />

                    <div v-if="isComplete(goal)" class="goal-card__check">
                      <v-icon size="16" color="white">mdi-check</v-icon>
                    </div>

                    <v-card-text>
                      <div class="d-flex align-start ga-4">
                        <div class="goal-card__cat">
                          <v-icon :icon="categoryConfig[goal.category].icon" />
                        </div>

                        <div class="flex-1 min-w-0">
                          <div class="d-flex align-start justify-space-between ga-2">
                            <div class="text-subtitle-1 font-weight-bold text-truncate">
                              {{ goal.name }}
                            </div>
                            <v-chip v-if="goal.status === 'pausada'" size="x-small" variant="outlined" class="chip-paused">
                              pausada
                            </v-chip>
                          </div>

                          <div class="d-flex align-center ga-2 mt-1">
                            <v-chip size="x-small" variant="tonal" class="chip-cat">
                              {{ categoryConfig[goal.category].label }}
                            </v-chip>
                          </div>
                        </div>
                      </div>

                      <div class="mt-5">
                        <div class="d-flex justify-space-between align-end mb-2">
                          <div class="goal-card__money">
                            {{ formatBRL(toNumber(goal.current_amount)) }}
                          </div>
                          <div class="text-body-2 text-medium-emphasis">
                            de {{ formatBRL(toNumber(goal.target_amount)) }}
                          </div>
                        </div>

                        <v-progress-linear
                          :model-value="percent(goal)"
                          height="10"
                          rounded
                          class="goal-progress"
                        />

                        <div class="d-flex justify-space-between mt-2">
                          <div class="text-caption text-medium-emphasis">
                            {{ progressText(goal) }}
                          </div>
                          <div class="text-caption font-weight-bold">
                            {{ percent(goal) }}%
                          </div>
                        </div>
                      </div>

                      <div v-if="daysLeft(goal) !== null && !isComplete(goal)" class="text-caption text-medium-emphasis mt-3">
                        {{ daysLeftText(goal) }}
                      </div>
                    </v-card-text>
                  </v-card>
                </div>
              </TransitionGroup>
            </section>

            <section v-if="completedGoals.length">
              <div class="text-subtitle-1 font-weight-bold mb-4">Metas Concluídas 🎉</div>

              <div class="goals-grid">
                <div v-for="goal in completedGoals" :key="goal.id" class="goal-wrap">
                  <v-card
                    class="goal-card"
                    :class="`cat-${goal.category}`"
                    rounded="xl"
                    variant="elevated"
                    @click="auth.isCoachOrAdmin ? openAddMoney(goal) : null"
                  >
                    <div class="goal-card__topbar" style="width: 100%" />
                    <div class="goal-card__check">
                      <v-icon size="16" color="white">mdi-check</v-icon>
                    </div>

                    <v-card-text>
                      <div class="d-flex align-start ga-4">
                        <div class="goal-card__cat">
                          <v-icon :icon="categoryConfig[goal.category].icon" />
                        </div>

                        <div class="flex-1 min-w-0">
                          <div class="text-subtitle-1 font-weight-bold text-truncate">
                            {{ goal.name }}
                          </div>
                          <div class="d-flex align-center ga-2 mt-1">
                            <v-chip size="x-small" variant="tonal" class="chip-cat">
                              {{ categoryConfig[goal.category].label }}
                            </v-chip>
                          </div>
                        </div>
                      </div>

                      <div class="mt-5">
                        <div class="d-flex justify-space-between align-end mb-2">
                          <div class="goal-card__money">
                            {{ formatBRL(toNumber(goal.current_amount)) }}
                          </div>
                          <div class="text-body-2 text-medium-emphasis">
                            de {{ formatBRL(toNumber(goal.target_amount)) }}
                          </div>
                        </div>

                        <v-progress-linear :model-value="100" height="10" rounded class="goal-progress" color="success" />

                        <div class="d-flex justify-space-between mt-2">
                          <div class="text-caption text-medium-emphasis">Meta atingida! 🎉</div>
                          <div class="text-caption font-weight-bold">100%</div>
                        </div>
                      </div>
                    </v-card-text>
                  </v-card>
                </div>
              </div>
            </section>
          </template>
        </template>
      </v-container>
    </main>

    <v-dialog v-model="newGoalOpen" max-width="720">
      <v-card rounded="xl">
        <v-card-title class="text-h6 font-weight-bold">Nova Meta</v-card-title>
        <v-card-text>
          <v-alert v-if="createError" type="error" variant="tonal" class="mb-3">{{ createError }}</v-alert>

          <v-row density="comfortable">
            <v-col cols="12">
              <v-text-field
                v-model="newGoalForm.name"
                label="Nome da meta"
                variant="outlined"
                density="comfortable"
                placeholder="Ex: Viagem para Europa"
                clearable
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="newGoalForm.target_amount"
                label="Valor alvo (R$)"
                variant="outlined"
                density="comfortable"
                type="number"
                inputmode="decimal"
                placeholder="5000.00"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="newGoalForm.category"
                label="Categoria"
                variant="outlined"
                density="comfortable"
                :items="categoryItems"
                item-title="title"
                item-value="value"
              >
                <template #selection="{ item }">
                  <div class="d-flex align-center ga-2">
                    <v-icon :icon="item.icon" size="18" />
                    <span>{{ item.title }}</span>
                  </div>
                </template>
                <template #item="{ props, item }">
                  <v-list-item v-bind="props">
                    <template #prepend>
                      <v-icon :icon="item.icon" />
                    </template>
                    <v-list-item-title>{{ item.title }}</v-list-item-title>
                  </v-list-item>
                </template>
              </v-select>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="newGoalForm.deadline"
                label="Prazo (opcional)"
                variant="outlined"
                density="comfortable"
                type="date"
              />
            </v-col>
            <v-col cols="12">
              <v-textarea
                v-model="newGoalForm.notes"
                label="Notas (opcional)"
                variant="outlined"
                density="comfortable"
                auto-grow
                rows="2"
                placeholder="Detalhes sobre sua meta..."
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="px-4 pb-4">
          <v-spacer />
          <v-btn variant="tonal" @click="newGoalOpen = false">Cancelar</v-btn>
          <v-btn
            class="btn-create-goal"
            :loading="creatingGoal"
            :disabled="!canCreateGoal"
            @click="createGoal"
          >
            {{ creatingGoal ? 'Criando...' : 'Criar Meta' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="moneyOpen" max-width="560">
      <v-card rounded="xl">
        <v-card-title class="text-h6 font-weight-bold">
          {{ selectedGoal?.name }}
        </v-card-title>
        <v-card-text>
          <v-alert v-if="txError" type="error" variant="tonal" class="mb-3">{{ txError }}</v-alert>

          <v-tabs v-model="moneyType" density="comfortable" class="mb-4">
            <v-tab value="deposito">
              <v-icon start size="18">mdi-arrow-down-circle</v-icon>
              Depositar
            </v-tab>
            <v-tab value="retirada">
              <v-icon start size="18">mdi-arrow-up-circle</v-icon>
              Retirar
            </v-tab>
          </v-tabs>

          <v-text-field
            v-model="moneyAmount"
            class="money-input"
            type="number"
            inputmode="decimal"
            label="Valor (R$)"
            variant="outlined"
            density="comfortable"
            placeholder="0.00"
            :max="moneyType === 'retirada' ? maxWithdraw : undefined"
          />

          <div class="quick-row">
            <v-btn
              v-for="qa in quickAmounts"
              :key="qa"
              variant="tonal"
              rounded="pill"
              size="small"
              class="quick-btn"
              @click="moneyAmount = String(qa)"
            >
              R$ {{ qa }}
            </v-btn>
          </div>

          <v-text-field
            v-model="moneyNote"
            label="Nota (opcional)"
            variant="outlined"
            density="comfortable"
            placeholder="Ex: Salário do mês"
            class="mt-3"
          />

          <v-btn
            block
            class="mt-4"
            :class="moneyType === 'deposito' ? 'btn-money btn-money--deposit' : 'btn-money btn-money--withdraw'"
            :loading="creatingTx"
            :disabled="!canSaveTx"
            @click="saveTransaction"
          >
            {{ moneyButtonText }}
          </v-btn>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { http } from '../api/http'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

type GoalCategory =
  | 'viagem'
  | 'tecnologia'
  | 'casa'
  | 'carro'
  | 'educacao'
  | 'saude'
  | 'emergencia'
  | 'outro'

type GoalStatus = 'ativa' | 'concluida' | 'pausada'

type Goal = {
  id: number
  name: string
  target_amount: string
  current_amount: string
  category: GoalCategory
  deadline: string | null
  notes: string
  status: GoalStatus
}

type TransactionPayload = {
  goal_id: number
  amount: number
  type: 'deposito' | 'retirada'
  note: string
}

const categoryConfig: Record<GoalCategory, { label: string; icon: string }> = {
  viagem: { label: 'Viagem', icon: 'mdi-airplane' },
  tecnologia: { label: 'Tecnologia', icon: 'mdi-laptop' },
  casa: { label: 'Casa', icon: 'mdi-home' },
  carro: { label: 'Carro', icon: 'mdi-car' },
  educacao: { label: 'Educação', icon: 'mdi-school' },
  saude: { label: 'Saúde', icon: 'mdi-heart' },
  emergencia: { label: 'Emergência', icon: 'mdi-shield-alert' },
  outro: { label: 'Outro', icon: 'mdi-sparkles' },
}

const categoryItems = Object.entries(categoryConfig).map(([value, cfg]) => ({
  value,
  title: cfg.label,
  icon: cfg.icon,
}))

const goals = ref<Goal[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const newGoalOpen = ref(false)
const creatingGoal = ref(false)
const createError = ref<string | null>(null)
const newGoalForm = ref({
  name: '',
  target_amount: '',
  category: '' as '' | GoalCategory,
  deadline: '',
  notes: '',
})

const selectedGoal = ref<Goal | null>(null)
const moneyOpen = ref(false)
const moneyAmount = ref('')
const moneyType = ref<'deposito' | 'retirada'>('deposito')
const moneyNote = ref('')
const creatingTx = ref(false)
const txError = ref<string | null>(null)

const quickAmounts = [10, 25, 50, 100, 200, 500]

function toNumber(v: string | number | null | undefined): number {
  const n = typeof v === 'number' ? v : Number(String(v ?? '0').replace(',', '.'))
  return Number.isFinite(n) ? n : 0
}

function formatBRL(v: number): string {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v)
}

function percent(goal: Goal): number {
  const target = toNumber(goal.target_amount)
  const current = toNumber(goal.current_amount)
  if (!target || target <= 0) return 0
  const p = Math.round((current / target) * 100)
  return Math.max(0, Math.min(100, Number.isFinite(p) ? p : 0))
}

function isComplete(goal: Goal): boolean {
  return goal.status === 'concluida' || percent(goal) >= 100
}

function progressText(goal: Goal): string {
  const target = toNumber(goal.target_amount)
  const current = toNumber(goal.current_amount)
  const remaining = Math.max(target - current, 0)
  return isComplete(goal) ? 'Meta atingida! 🎉' : `Faltam ${formatBRL(remaining)}`
}

function diffInDays(deadlineISO: string): number {
  const end = new Date(`${deadlineISO}T00:00:00`)
  const start = new Date()
  const startDay = new Date(start.getFullYear(), start.getMonth(), start.getDate())
  const ms = end.getTime() - startDay.getTime()
  return Math.round(ms / (1000 * 60 * 60 * 24))
}

function daysLeft(goal: Goal): number | null {
  if (!goal.deadline) return null
  const d = diffInDays(goal.deadline)
  return Number.isFinite(d) ? d : null
}

function daysLeftText(goal: Goal): string {
  const d = daysLeft(goal)
  if (d === null) return ''
  if (d > 0) return `${d} dias restantes`
  if (d === 0) return 'Vence hoje'
  return 'Prazo expirado'
}

const activeGoals = computed(() => goals.value.filter((g) => !isComplete(g)))
const completedGoals = computed(() => goals.value.filter((g) => isComplete(g)))

const totalSaved = computed(() => goals.value.reduce((sum, g) => sum + toNumber(g.current_amount), 0))
const totalTarget = computed(() => goals.value.reduce((sum, g) => sum + toNumber(g.target_amount), 0))

const canCreateGoal = computed(() => {
  return Boolean(newGoalForm.value.name.trim()) &&
    Boolean(newGoalForm.value.target_amount) &&
    Boolean(newGoalForm.value.category)
})

async function fetchGoals() {
  loading.value = true
  error.value = null
  try {
    const { data } = await http.get('/cashbox/goals/', { params: { ordering: '-created_at' } })
    goals.value = Array.isArray(data) ? (data as Goal[]) : (data?.results ?? [])
  } catch (e: any) {
    const status = e?.response?.status
    error.value = status ? `Falha ao carregar metas (HTTP ${status}).` : 'Falha ao carregar metas.'
    goals.value = []
  } finally {
    loading.value = false
  }
}


function openNewGoal() {
  createError.value = null
  newGoalOpen.value = true
}

async function createGoal() {
  if (!canCreateGoal.value) return
  creatingGoal.value = true
  createError.value = null
  try {
    const payload = {
      name: newGoalForm.value.name.trim(),
      target_amount: String(toNumber(newGoalForm.value.target_amount)),
      category: newGoalForm.value.category,
      deadline: newGoalForm.value.deadline || null,
      notes: newGoalForm.value.notes || '',
      status: 'ativa',
    }
    const { data } = await http.post('/cashbox/goals/', payload)
    goals.value = [data as Goal, ...goals.value]
    newGoalForm.value = { name: '', target_amount: '', category: '', deadline: '', notes: '' }
    newGoalOpen.value = false
  } catch (e: any) {
    const status = e?.response?.status
    createError.value = status ? `Falha ao criar meta (HTTP ${status}).` : 'Falha ao criar meta.'
  } finally {
    creatingGoal.value = false
  }
}

function openAddMoney(goal: Goal) {
  selectedGoal.value = goal
  moneyOpen.value = true
  moneyType.value = 'deposito'
  moneyAmount.value = ''
  moneyNote.value = ''
  txError.value = null
}

const maxWithdraw = computed(() => (selectedGoal.value ? toNumber(selectedGoal.value.current_amount) : 0))

const canSaveTx = computed(() => {
  const amount = toNumber(moneyAmount.value)
  if (!selectedGoal.value) return false
  if (!Number.isFinite(amount) || amount <= 0) return false
  if (moneyType.value === 'retirada') return amount <= maxWithdraw.value
  return true
})

const moneyButtonText = computed(() => {
  const amount = toNumber(moneyAmount.value)
  const formatted = formatBRL(amount)
  return creatingTx.value
    ? 'Salvando...'
    : moneyType.value === 'deposito'
      ? `Depositar ${formatted}`
      : `Retirar ${formatted}`
})

async function saveTransaction() {
  if (!selectedGoal.value || !canSaveTx.value) return
  creatingTx.value = true
  txError.value = null

  const goal = selectedGoal.value
  const amount = toNumber(moneyAmount.value)

  const payload: TransactionPayload = {
    goal_id: goal.id,
    amount,
    type: moneyType.value,
    note: moneyNote.value,
  }

  try {
    const { data } = await http.post(`/cashbox/goals/${goal.id}/transactions/`, {
      amount: String(amount),
      type: payload.type,
      note: payload.note,
    })

    const updated = (data?.goal ?? null) as Goal | null
    if (updated) {
      goals.value = goals.value.map((g) => (g.id === updated.id ? updated : g))
      selectedGoal.value = updated
    } else {
      const current = toNumber(goal.current_amount)
      const newAmount = payload.type === 'deposito' ? current + amount : Math.max(current - amount, 0)
      const newStatus: GoalStatus =
        goal.status === 'concluida' ? 'concluida' : (newAmount >= toNumber(goal.target_amount) ? 'concluida' : goal.status)
      goals.value = goals.value.map((g) =>
        g.id === goal.id ? { ...g, current_amount: String(newAmount), status: newStatus } : g,
      )
    }

    moneyAmount.value = ''
    moneyNote.value = ''
    moneyOpen.value = false
  } catch (e: any) {
    const status = e?.response?.status
    txError.value = status ? `Falha ao salvar (HTTP ${status}).` : 'Falha ao salvar.'
  } finally {
    creatingTx.value = false
  }
}

onMounted(fetchGoals)
</script>

<style scoped>
.cofrinho-page {
  min-height: 100vh;
  background: linear-gradient(
    180deg,
    rgba(var(--v-theme-cashViolet50), 1) 0%,
    rgba(var(--v-theme-surface), 1) 60%,
    rgba(var(--v-theme-surface), 1) 100%
  );
}

.cofrinho-container {
  max-width: 980px;
}

.cofrinho-header {
  position: sticky;
  top: 0;
  z-index: 3;
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  background: rgba(var(--v-theme-surface), 0.78);
  backdrop-filter: blur(14px);
}

.brand-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-cashViolet500), 1),
    rgba(var(--v-theme-cashIndigo600), 1)
  );
}

.btn-new-goal {
  color: white;
  background: linear-gradient(
    90deg,
    rgba(var(--v-theme-cashViolet500), 1),
    rgba(var(--v-theme-cashIndigo600), 1)
  );
  box-shadow: 0 12px 26px rgba(var(--v-theme-cashViolet500), 0.18);
}

.btn-create-goal {
  color: white;
  background: linear-gradient(
    90deg,
    rgba(var(--v-theme-cashViolet500), 1),
    rgba(var(--v-theme-cashIndigo600), 1)
  );
}

.spinner {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  border: 4px solid rgba(var(--v-theme-cashViolet500), 0.15);
  border-top-color: rgba(var(--v-theme-cashViolet500), 1);
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 72px 16px;
}

.empty__circle {
  width: 108px;
  height: 108px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(var(--v-theme-cashViolet500), 1);
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-cashViolet500), 0.14),
    rgba(var(--v-theme-cashIndigo600), 0.12)
  );
}

.summary {
  color: white;
}

.summary__icon {
  opacity: 0.85;
  margin-bottom: 10px;
}

.summary__label {
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  opacity: 0.72;
  font-weight: 600;
}

.summary__value {
  font-size: 22px;
  font-weight: 800;
  margin-top: 4px;
}

.summary--violet {
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-cashViolet500), 1),
    rgba(var(--v-theme-cashIndigo600), 1)
  );
}

.summary--blue {
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-cashSky400), 1),
    rgba(var(--v-theme-cashBlue600), 1)
  );
}

.summary--amber {
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-cashAmber500), 1),
    rgba(var(--v-theme-cashOrange600), 1)
  );
}

.summary--green {
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-cashEmerald500), 1),
    rgba(var(--v-theme-cashGreen600), 1)
  );
}

.goals-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

@media (min-width: 600px) {
  .goals-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1280px) {
  .goals-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.goal-wrap {
  width: 100%;
}

.goal-card {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease;
}

.goal-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 40px rgba(var(--v-theme-on-surface), 0.08);
}

.goal-card__topbar {
  position: absolute;
  left: 0;
  top: 0;
  height: 8px;
  background: linear-gradient(90deg, rgba(var(--goal-accent), 1), rgba(var(--goal-accent), 0.55));
  transition: width 0.6s ease;
}

.goal-card__check {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 26px;
  height: 26px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--v-theme-cashEmerald500), 1);
}

.goal-card__cat {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--goal-accent), 0.12);
  color: rgba(var(--goal-accent), 1);
  transition: transform 0.25s ease;
}

.goal-card:hover .goal-card__cat {
  transform: scale(1.10);
}

.chip-cat {
  border: 0;
  background: rgba(var(--goal-accent), 0.14);
  color: rgba(var(--goal-accent), 1);
}

.chip-paused {
  border-color: rgba(var(--v-theme-cashAmber500), 0.65);
  color: rgba(var(--v-theme-cashOrange600), 1);
}

.goal-card__money {
  font-size: 22px;
  font-weight: 800;
}

.goal-progress :deep(.v-progress-linear__background) {
  opacity: 1;
  background: rgba(var(--v-theme-on-surface), 0.07);
}

.goal-progress :deep(.v-progress-linear__determinate) {
  background: rgba(var(--goal-accent), 1);
}

.goal-enter-active,
.goal-leave-active {
  transition: all 0.25s ease;
}

.goal-enter-from,
.goal-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.money-input :deep(input) {
  font-size: 24px;
  font-weight: 800;
  text-align: center;
  height: 56px;
}

.quick-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-btn {
  font-weight: 700;
}

.btn-money {
  color: white;
  font-weight: 800;
}

.btn-money--deposit {
  background: linear-gradient(90deg, rgba(var(--v-theme-cashEmerald500), 1), rgba(var(--v-theme-cashGreen600), 1));
}

.btn-money--withdraw {
  background: linear-gradient(90deg, rgba(var(--v-theme-cashRose400), 1), rgba(var(--v-theme-cashRed600), 1));
}

.cat-viagem {
  --goal-accent: var(--v-theme-cashSky400);
}
.cat-tecnologia {
  --goal-accent: var(--v-theme-cashViolet500);
}
.cat-casa {
  --goal-accent: var(--v-theme-cashAmber500);
}
.cat-carro {
  --goal-accent: var(--v-theme-cashEmerald500);
}
.cat-educacao {
  --goal-accent: var(--v-theme-cashIndigo600);
}
.cat-saude {
  --goal-accent: var(--v-theme-cashPink600);
}
.cat-emergencia {
  --goal-accent: var(--v-theme-cashRed600);
}
.cat-outro {
  --goal-accent: var(--v-theme-cashSlate600);
}
</style>
