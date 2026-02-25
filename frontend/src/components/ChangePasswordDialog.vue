<template>
  <v-dialog v-model="model" max-width="520">
    <v-card>
      <v-card-title>Trocar senha</v-card-title>

      <v-card-text>
        <v-alert v-if="error" type="error" variant="tonal" class="mb-3">
          {{ error }}
        </v-alert>
        <v-alert v-if="success" type="success" variant="tonal" class="mb-3">
          Senha alterada com sucesso.
        </v-alert>

        <v-form @submit.prevent="onSubmit">
          <v-text-field
            v-model="form.current_password"
            label="Senha atual"
            type="password"
            autocomplete="current-password"
            :disabled="loading"
          />

          <v-text-field
            v-model="form.new_password"
            label="Nova senha"
            type="password"
            autocomplete="new-password"
            :disabled="loading"
          />

          <v-text-field
            v-model="form.confirm_password"
            label="Confirmar nova senha"
            type="password"
            autocomplete="new-password"
            :disabled="loading"
          />
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" :disabled="loading" @click="onClose">Cancelar</v-btn>
        <v-btn color="primary" :loading="loading" @click="onSubmit">Salvar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
export default {
  name: 'ChangePasswordDialog',
}
</script>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { http } from '../api/http'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>()

const model = computed({
  get: () => props.modelValue,
  set: (v: boolean) => emit('update:modelValue', v),
})

const loading = ref(false)
const error = ref<string | null>(null)
const success = ref(false)

const form = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
})

function reset() {
  form.current_password = ''
  form.new_password = ''
  form.confirm_password = ''
  error.value = null
  success.value = false
  loading.value = false
}

watch(
  () => props.modelValue,
  (open) => {
    if (open) reset()
  },
)

function onClose() {
  model.value = false
}

async function onSubmit() {
  if (loading.value) return
  error.value = null
  success.value = false

  if (!form.current_password || !form.new_password || !form.confirm_password) {
    error.value = 'Preencha todos os campos.'
    return
  }
  if (form.new_password !== form.confirm_password) {
    error.value = 'A confirmação não confere.'
    return
  }

  loading.value = true
  try {
    await http.post('/accounts/change-password/', {
      current_password: form.current_password,
      new_password: form.new_password,
      confirm_password: form.confirm_password,
    })
    success.value = true

    form.current_password = ''
    form.new_password = ''
    form.confirm_password = ''

    setTimeout(() => {
      onClose()
    }, 900)
  } catch (e: any) {
    const msg =
      e?.response?.data?.current_password ||
      e?.response?.data?.confirm_password ||
      e?.response?.data?.detail ||
      'Não foi possível alterar a senha.'
    error.value = Array.isArray(msg) ? msg.join(' ') : String(msg)
  } finally {
    loading.value = false
  }
}
</script>
