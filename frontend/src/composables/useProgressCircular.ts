import { onBeforeUnmount, ref, watch, type Ref } from 'vue'

type Options = {
  /** Intervalo do timer em ms (padrão: 100ms). */
  tickMs?: number
  /** Incremento de progresso por tick (padrão: 2 => 0→100 em ~5s). */
  step?: number
}

export function useProgressCircular(loading: Ref<boolean>, options: Options = {}) {
  const progressValue = ref(0)
  const tickMs = options.tickMs ?? 100
  const step = options.step ?? 2

  let intervalId = -1

  function stop() {
    if (intervalId !== -1) {
      window.clearInterval(intervalId)
      intervalId = -1
    }
    progressValue.value = 0
  }

  function start() {
    stop()
    intervalId = window.setInterval(() => {
      if (progressValue.value >= 100) {
        progressValue.value = 0
        return
      }
      progressValue.value += step
    }, tickMs)
  }

  watch(
    loading,
    (isLoading) => {
      if (isLoading) start()
      else stop()
    },
    { immediate: true },
  )

  onBeforeUnmount(() => stop())

  return { progressValue }
}
