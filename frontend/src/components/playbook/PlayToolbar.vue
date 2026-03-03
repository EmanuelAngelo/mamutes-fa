<template>
  <v-card variant="tonal" rounded="xl" class="toolbar-card">
    <v-card-text>
      <div class="text-caption text-medium-emphasis font-weight-bold mb-2">Ferramenta</div>
      <div class="d-flex ga-2">
        <v-btn
          size="small"
          class="flex-grow-1"
          :variant="mode === 'move' ? 'flat' : 'tonal'"
          :color="mode === 'move' ? 'primary' : undefined"
          @click="$emit('update:mode', 'move')"
        >
          <v-icon start size="16">mdi-cursor-move</v-icon>
          Mover
        </v-btn>
        <v-btn
          size="small"
          class="flex-grow-1"
          :variant="mode === 'route' ? 'flat' : 'tonal'"
          :color="mode === 'route' ? 'warning' : undefined"
          @click="$emit('update:mode', 'route')"
        >
          <v-icon start size="16">mdi-pencil</v-icon>
          Rota
        </v-btn>
        <v-btn
          size="small"
          class="flex-grow-1"
          :variant="mode === 'erase' ? 'flat' : 'tonal'"
          :color="mode === 'erase' ? 'error' : undefined"
          @click="$emit('update:mode', 'erase')"
        >
          <v-icon start size="16">mdi-eraser</v-icon>
          Apagar
        </v-btn>
      </div>

      <div v-if="drawing" class="mt-3 pa-3 rounded-lg drawing-box">
        <div class="text-caption font-weight-bold" style="opacity: 0.9">Desenhando rota…</div>
        <div class="d-flex ga-2 mt-2">
          <v-btn size="small" class="flex-grow-1" color="warning" variant="flat" @click="$emit('finishRoute')">
            Finalizar
          </v-btn>
          <v-btn size="small" class="flex-grow-1" variant="tonal" @click="$emit('cancelRoute')">
            Cancelar
          </v-btn>
        </div>
      </div>

      <div v-if="mode === 'route'" class="mt-4">
        <div class="text-caption text-medium-emphasis font-weight-bold mb-2">Cor da rota</div>
        <div class="d-flex flex-wrap ga-2">
          <button
            v-for="c in colors"
            :key="c.value"
            type="button"
            class="color-dot"
            :class="{ 'color-dot--active': routeColor === c.value }"
            :style="{ backgroundColor: c.preview }"
            :title="c.label"
            @click="$emit('update:routeColor', c.value)"
          />
        </div>

        <div class="text-caption text-medium-emphasis font-weight-bold mb-2 mt-4">Tipo</div>
        <div class="d-flex ga-2">
          <v-btn
            v-for="t in types"
            :key="t.value"
            size="small"
            class="flex-grow-1"
            :variant="routeType === t.value ? 'flat' : 'tonal'"
            :color="routeType === t.value ? 'secondary' : undefined"
            @click="$emit('update:routeType', t.value)"
          >
            {{ t.label }}
          </v-btn>
        </div>
      </div>

      <v-divider class="my-4" />

      <v-btn block variant="tonal" rounded="xl" @click="$emit('clearRoutes')">
        <v-icon start size="16">mdi-rotate-left</v-icon>
        Limpar rotas
      </v-btn>

      <v-btn block color="primary" variant="flat" rounded="xl" class="mt-2" :loading="saving" @click="$emit('save')">
        <v-icon start size="16">mdi-content-save</v-icon>
        {{ saving ? 'Salvando…' : 'Salvar jogada' }}
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
export default {
  name: 'PlayToolbar',
}
</script>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  mode: 'move' | 'route' | 'erase'
  routeColor: string
  routeType: string
  drawing: boolean
  saving: boolean
}>()

defineEmits<{
  (e: 'update:mode', value: 'move' | 'route' | 'erase'): void
  (e: 'update:routeColor', value: string): void
  (e: 'update:routeType', value: string): void
  (e: 'finishRoute'): void
  (e: 'cancelRoute'): void
  (e: 'clearRoutes'): void
  (e: 'save'): void
}>()

function readThemeRgb(key: string): string {
  if (typeof window === 'undefined') return 'rgb(0, 0, 0)'
  const raw = getComputedStyle(document.documentElement)
    .getPropertyValue(`--v-theme-${key}`)
    .trim()
  if (!raw) return 'rgb(0, 0, 0)'
  return `rgb(${raw})`
}

const colors = computed(() => {
  const warning = readThemeRgb('warning')
  const error = readThemeRgb('error')
  const info = readThemeRgb('info')
  const success = readThemeRgb('success')
  const primary = readThemeRgb('primary')
  return [
    { value: 'warning', label: 'Amarelo', preview: warning },
    { value: 'error', label: 'Vermelho', preview: error },
    { value: 'info', label: 'Azul', preview: info },
    { value: 'success', label: 'Verde', preview: success },
    { value: 'primary', label: 'Roxo', preview: primary },
    { value: 'white', label: 'Branco', preview: 'rgb(255, 255, 255)' },
  ]
})

const types = [
  { value: 'route', label: 'Rota' },
  { value: 'run', label: 'Corrida' },
  { value: 'block', label: 'Bloqueio' },
]

// just to satisfy unused-props linting in some setups
computed(() => props.mode)
</script>

<style scoped>
.toolbar-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.10);
}

.drawing-box {
  border: 1px solid rgba(var(--v-theme-warning), 0.35);
  background: rgba(var(--v-theme-warning), 0.10);
}

.color-dot {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  border: 2px solid rgba(var(--v-theme-on-surface), 0.25);
  cursor: pointer;
}

.color-dot--active {
  border-color: rgba(var(--v-theme-on-surface), 0.85);
}
</style>
