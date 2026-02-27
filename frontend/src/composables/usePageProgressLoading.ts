import { onBeforeUnmount, ref } from 'vue'

type Options = {
  /** Tempo mínimo (ms) que o loading deve ficar visível. */
  minDurationMs?: number
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * Loading de página com v-progress-circular determinístico.
 * - Progresso vai de 0 a 100 em ~5s (incremento de 10 a cada 500ms).
 * - `stop()` respeita um tempo mínimo para manter o loading visível.
 */
export function usePageProgressLoading(options: Options = {}) {
  const minDurationMs = options.minDurationMs ?? 5000

  const loading = ref(true)
  const value = ref(0)

  let startedAt = 0
  let interval: any = null

  function clear() {
    if (interval) {
      clearInterval(interval)
      interval = null
    }
  }

  function start() {
    startedAt = Date.now()
    loading.value = true
    value.value = 0

    clear()
    interval = setInterval(() => {
      if (value.value >= 100) value.value = 0
      else value.value += 10
    }, 500)
  }

  async function stop(override?: { minDurationMs?: number }) {
    const targetMin = override?.minDurationMs ?? minDurationMs
    const elapsed = Date.now() - startedAt
    const remaining = Math.max(0, targetMin - elapsed)
    if (remaining) await sleep(remaining)

    clear()
    loading.value = false
  }

  onBeforeUnmount(() => {
    clear()
  })

  return {
    loading,
    value,
    start,
    stop,
  }
}
