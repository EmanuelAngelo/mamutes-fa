<template>
  <v-menu v-model="menu" :close-on-content-click="false" location="bottom">
    <template #activator="{ props: activatorProps }">
      <v-text-field
        v-bind="activatorProps"
        :model-value="modelValue"
        :label="label"
        :disabled="disabled"
        readonly
        clearable
        prepend-inner-icon="mdi-calendar"
        @click:clear="onClear"
      />
    </template>

    <v-date-picker
      v-model="internal"
      @update:model-value="onPick"
    />
  </v-menu>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: string
  label: string
  disabled?: boolean
}>()

const emit = defineEmits<{ (e: 'update:modelValue', v: string): void }>()

const menu = ref(false)
const internal = ref<string | undefined>(props.modelValue || undefined)

watch(
  () => props.modelValue,
  (v) => {
    internal.value = v || undefined
  },
)

watch(menu, (open) => {
  if (open) internal.value = props.modelValue || undefined
})

function onPick(v: any) {
  const value = Array.isArray(v) ? v[0] : v
  if (typeof value === 'string') {
    emit('update:modelValue', value)
  }
  menu.value = false
}

function onClear() {
  emit('update:modelValue', '')
}
</script>

<script lang="ts">
export default {
  name: 'DateField',
}
</script>
