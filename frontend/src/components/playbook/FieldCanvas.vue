<template>
  <div ref="containerRef" class="field-canvas">
    <canvas
      ref="canvasRef"
      class="field-canvas__canvas"
      :class="{ 'field-canvas__canvas--readonly': readOnly }"
      :width="size.width"
      :height="size.height"
      @pointerdown="handlePointerDown"
      @pointermove="handlePointerMove"
      @pointerup="handlePointerUp"
      @pointercancel="handlePointerUp"
      @pointerleave="handlePointerUp"
      @dblclick="handleDoubleClick"
    />

    <div
      v-if="mode === 'route' && drawingRoute && drawingRoute.points?.length"
      class="field-canvas__hint"
    >
      Clique para adicionar pontos • Duplo-clique para finalizar
    </div>
  </div>
</template>

<script lang="ts">
export default {
  name: 'FieldCanvas',
}
</script>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

type Player = {
  id: string
  x: number
  y: number
  role?: string
  team?: string
  label?: string
}

type RoutePoint = { x: number; y: number }

type Route = {
  player_id: string
  points: RoutePoint[]
  type?: string
  color?: string
}

type DrawingRoute = Route | null

const BASE_W = 500
const BASE_H = 700

const props = defineProps<{
  players: Player[]
  routes: Route[]
  selectedPlayerId: string | null
  mode: 'move' | 'route' | 'erase'
  routeColor: string
  routeType: string
  drawingRoute: DrawingRoute
  readOnly?: boolean
}>()

const readOnly = computed(() => Boolean(props.readOnly))

const emit = defineEmits<{
  (e: 'playerMove', id: string, x: number, y: number): void
  (e: 'playerSelect', id: string | null): void
  (e: 'routeAdd', route: Route): void
  (e: 'routeErase', index: number): void
  (e: 'update:drawingRoute', value: DrawingRoute): void
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const containerRef = ref<HTMLElement | null>(null)

const size = ref({ width: 500, height: 700 })
const draggingId = ref<string | null>(null)

const scale = computed(() => {
  const sx = size.value.width / BASE_W
  const sy = size.value.height / BASE_H
  return { sx, sy }
})

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n))
}

function readThemeRgb(key: string): string {
  if (typeof window === 'undefined') return 'rgb(0, 0, 0)'
  const raw = getComputedStyle(document.documentElement)
    .getPropertyValue(`--v-theme-${key}`)
    .trim()
  if (!raw) return 'rgb(0, 0, 0)'
  return `rgb(${raw})`
}

function withAlpha(rgb: string, alpha: number) {
  const match = rgb.match(/rgb\(([^)]+)\)/)
  if (!match) return rgb
  return `rgba(${match[1]}, ${alpha})`
}

function resolveColor(color: string | undefined): string {
  if (!color) return readThemeRgb('warning')
  if (color.startsWith('#') || color.startsWith('rgb')) return color
  switch (color) {
    case 'warning':
      return readThemeRgb('warning')
    case 'error':
      return readThemeRgb('error')
    case 'info':
      return readThemeRgb('info')
    case 'success':
      return readThemeRgb('success')
    case 'primary':
      return readThemeRgb('primary')
    case 'white':
      return 'rgb(255, 255, 255)'
    default:
      return readThemeRgb('warning')
  }
}

function drawField(ctx: CanvasRenderingContext2D, w: number, h: number) {
  const field = readThemeRgb('success')
  const endzone = withAlpha(field, 0.55)
  const line = withAlpha(readThemeRgb('on-surface'), 0.20)
  const yardLine = withAlpha(readThemeRgb('on-surface'), 0.45)

  ctx.fillStyle = withAlpha(field, 0.65)
  ctx.fillRect(0, 0, w, h)

  const endzoneH = h * 0.1
  ctx.fillStyle = endzone
  ctx.fillRect(0, 0, w, endzoneH)
  ctx.fillRect(0, h - endzoneH, w, endzoneH)

  ctx.save()
  ctx.font = `bold ${Math.max(14, w * 0.04)}px Roboto, sans-serif`
  ctx.fillStyle = withAlpha('rgb(255, 255, 255)', 0.12)
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('END ZONE', w / 2, endzoneH / 2)
  ctx.fillText('END ZONE', w / 2, h - endzoneH / 2)
  ctx.restore()

  const playableH = h - 2 * endzoneH
  const yardLines = 8
  ctx.strokeStyle = line
  ctx.lineWidth = 1
  for (let i = 0; i <= yardLines; i++) {
    const y = endzoneH + (playableH / yardLines) * i
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(w, y)
    ctx.stroke()
  }

  const centerY = endzoneH + playableH / 2
  ctx.strokeStyle = yardLine
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(0, centerY)
  ctx.lineTo(w, centerY)
  ctx.stroke()

  // hashes
  ctx.strokeStyle = line
  ctx.lineWidth = 1
  for (let i = 1; i < yardLines; i++) {
    const y = endzoneH + (playableH / yardLines) * i
    ctx.beginPath()
    ctx.moveTo(w * 0.33, y - 5)
    ctx.lineTo(w * 0.33, y + 5)
    ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(w * 0.67, y - 5)
    ctx.lineTo(w * 0.67, y + 5)
    ctx.stroke()
  }

  ctx.strokeStyle = withAlpha(readThemeRgb('on-surface'), 0.35)
  ctx.lineWidth = 3
  ctx.strokeRect(1.5, 1.5, w - 3, h - 3)

  // line of scrimmage (dashed)
  const losY = endzoneH + playableH * 0.65
  ctx.strokeStyle = withAlpha(readThemeRgb('warning'), 0.25)
  ctx.lineWidth = 2
  ctx.setLineDash([8, 6])
  ctx.beginPath()
  ctx.moveTo(0, losY)
  ctx.lineTo(w, losY)
  ctx.stroke()
  ctx.setLineDash([])
}

function drawPlayer(ctx: CanvasRenderingContext2D, p: Player, isSelected: boolean, isDragging: boolean) {
  const r = 16
  const team = p.team === 'defense' ? 'defense' : 'offense'
  const fill = resolveColor(team === 'offense' ? 'info' : 'error')

  // shadow
  ctx.beginPath()
  ctx.arc(p.x, p.y + 2, r + 1, 0, Math.PI * 2)
  ctx.fillStyle = withAlpha('rgb(0, 0, 0)', 0.25)
  ctx.fill()

  // body
  ctx.beginPath()
  ctx.arc(p.x, p.y, r, 0, Math.PI * 2)
  ctx.fillStyle = fill
  ctx.fill()

  ctx.strokeStyle = isSelected ? resolveColor('warning') : withAlpha('rgb(255,255,255)', 0.8)
  ctx.lineWidth = isSelected ? 3 : 1.5
  ctx.stroke()

  ctx.font = 'bold 11px Roboto, sans-serif'
  ctx.fillStyle = 'rgb(255, 255, 255)'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  const label = p.label || (p.role ? p.role.slice(0, 1).toUpperCase() : '?')
  ctx.fillText(label, p.x, p.y)

  if (isDragging) {
    ctx.beginPath()
    ctx.arc(p.x, p.y, r + 6, 0, Math.PI * 2)
    ctx.strokeStyle = withAlpha(resolveColor('warning'), 0.35)
    ctx.lineWidth = 2
    ctx.stroke()
  }
}

function drawRoute(ctx: CanvasRenderingContext2D, route: Route, isActive: boolean) {
  if (!route.points?.length) return
  const first = route.points[0]
  if (!first) return
  const color = resolveColor(route.color)
  ctx.strokeStyle = color
  ctx.lineWidth = isActive ? 3.5 : 2.5
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'

  if (route.type === 'block') ctx.setLineDash([4, 4])
  else ctx.setLineDash([])

  ctx.beginPath()
  ctx.moveTo(first.x, first.y)
  for (let i = 1; i < route.points.length; i++) {
    const pt = route.points[i]
    if (!pt) continue
    ctx.lineTo(pt.x, pt.y)
  }
  ctx.stroke()
  ctx.setLineDash([])

  if (route.points.length >= 2) {
    const lastIndex = route.points.length - 1
    const last = route.points[lastIndex]
    const prev = route.points[lastIndex - 1]
    if (!last || !prev) return
    const angle = Math.atan2(last.y - prev.y, last.x - prev.x)
    const arrowLen = 10
    ctx.fillStyle = color
    ctx.beginPath()
    ctx.moveTo(last.x, last.y)
    ctx.lineTo(last.x - arrowLen * Math.cos(angle - 0.4), last.y - arrowLen * Math.sin(angle - 0.4))
    ctx.lineTo(last.x - arrowLen * Math.cos(angle + 0.4), last.y - arrowLen * Math.sin(angle + 0.4))
    ctx.closePath()
    ctx.fill()
  }
}

function redraw() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)
  drawField(ctx, canvas.width, canvas.height)

  // scale stored base coords -> current canvas
  const { sx, sy } = scale.value
  const scaledRoutes = props.routes.map((r) => ({
    ...r,
    points: (r.points ?? []).map((pt) => ({ x: pt.x * sx, y: pt.y * sy })),
  }))

  for (const r of scaledRoutes) drawRoute(ctx, r, false)

  if (props.drawingRoute?.points?.length) {
    drawRoute(
      ctx,
      {
        ...props.drawingRoute,
        points: props.drawingRoute.points.map((pt) => ({ x: pt.x * sx, y: pt.y * sy })),
      },
      true,
    )
  }

  const scaledPlayers = props.players.map((p) => ({ ...p, x: p.x * sx, y: p.y * sy }))
  for (const p of scaledPlayers) {
    drawPlayer(ctx, p, p.id === props.selectedPlayerId, draggingId.value === p.id)
  }
}

function updateSize() {
  const el = containerRef.value
  if (!el) return
  const w = Math.max(260, el.clientWidth)
  const h = Math.min(w * 1.4, window.innerHeight * 0.75)
  size.value = { width: Math.round(w), height: Math.round(h) }
}

let ro: ResizeObserver | null = null

onMounted(() => {
  updateSize()
  ro = new ResizeObserver(() => updateSize())
  if (containerRef.value) ro.observe(containerRef.value)
  window.addEventListener('resize', updateSize)
})

onBeforeUnmount(() => {
  if (ro && containerRef.value) ro.unobserve(containerRef.value)
  ro = null
  window.removeEventListener('resize', updateSize)
})

watch(
  () => [props.players, props.routes, props.selectedPlayerId, props.drawingRoute, size.value.width, size.value.height, props.mode],
  () => redraw(),
  { deep: true, immediate: true },
)

function getBasePos(e: PointerEvent) {
  const canvas = canvasRef.value
  if (!canvas) return { x: 0, y: 0 }
  const rect = canvas.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const bx = (x / rect.width) * BASE_W
  const by = (y / rect.height) * BASE_H
  return { x: clamp(bx, 0, BASE_W), y: clamp(by, 0, BASE_H) }
}

function findPlayerAt(x: number, y: number) {
  return props.players.find((p) => Math.hypot(p.x - x, p.y - y) < 20)
}

function distPointToSegmentSq(px: number, py: number, ax: number, ay: number, bx: number, by: number): number {
  const abx = bx - ax
  const aby = by - ay
  const apx = px - ax
  const apy = py - ay
  const abLenSq = abx * abx + aby * aby
  if (abLenSq <= 1e-6) return apx * apx + apy * apy
  let t = (apx * abx + apy * aby) / abLenSq
  t = Math.max(0, Math.min(1, t))
  const cx = ax + t * abx
  const cy = ay + t * aby
  const dx = px - cx
  const dy = py - cy
  return dx * dx + dy * dy
}

function handlePointerDown(e: PointerEvent) {
  if (readOnly.value) return
  const canvas = canvasRef.value
  if (!canvas) return
  canvas.setPointerCapture(e.pointerId)

  const pos = getBasePos(e)
  const player = findPlayerAt(pos.x, pos.y)

  if (props.mode === 'move') {
    if (player) {
      draggingId.value = player.id
      emit('playerSelect', player.id)
    } else {
      emit('playerSelect', null)
    }
    return
  }

  if (props.mode === 'route') {
    if (player && !props.drawingRoute) {
      emit('playerSelect', player.id)
      emit('update:drawingRoute', {
        player_id: player.id,
        points: [{ x: player.x, y: player.y }],
        type: props.routeType,
        color: props.routeColor,
      })
      return
    }

    if (props.drawingRoute) {
      emit('update:drawingRoute', {
        ...props.drawingRoute,
        points: [...props.drawingRoute.points, { x: pos.x, y: pos.y }],
      })
    }
    return
  }

  if (props.mode === 'erase') {
    const threshold = 14
    const thSq = threshold * threshold
    let bestIdx = -1
    let bestDist = Number.POSITIVE_INFINITY

    for (let i = 0; i < props.routes.length; i++) {
      const r = props.routes[i]
      const pts = r?.points ?? []
      if (pts.length < 2) continue

      let minDist = Number.POSITIVE_INFINITY
      for (let j = 1; j < pts.length; j++) {
        const a = pts[j - 1]
        const b = pts[j]
        if (!a || !b) continue
        const d = distPointToSegmentSq(pos.x, pos.y, a.x, a.y, b.x, b.y)
        if (d < minDist) minDist = d
      }

      if (minDist < bestDist) {
        bestDist = minDist
        bestIdx = i
      }
    }

    if (bestIdx >= 0 && bestDist <= thSq) emit('routeErase', bestIdx)
  }
}

function handlePointerMove(e: PointerEvent) {
  if (readOnly.value) return
  if (props.mode !== 'move') return
  if (!draggingId.value) return
  const pos = getBasePos(e)
  emit('playerMove', draggingId.value, pos.x, pos.y)
}

function handlePointerUp() {
  draggingId.value = null
}

function handleDoubleClick(e: MouseEvent) {
  if (readOnly.value) return
  if (props.mode !== 'route') return
  if (!props.drawingRoute) return

  const pe = e as unknown as PointerEvent
  const pos = getBasePos(pe)
  const route: Route = {
    ...props.drawingRoute,
    points: [...props.drawingRoute.points, { x: pos.x, y: pos.y }],
  }
  emit('routeAdd', route)
  emit('update:drawingRoute', null)
}
</script>

<style scoped>
.field-canvas {
  position: relative;
  width: 100%;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.10);
}

.field-canvas__canvas {
  display: block;
  width: 100%;
  height: auto;
  touch-action: none;
  cursor: crosshair;
}

.field-canvas__canvas--readonly {
  cursor: default;
}

.field-canvas__hint {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.55);
  color: rgba(255, 255, 255, 0.92);
  font-size: 12px;
  backdrop-filter: blur(10px);
}
</style>
