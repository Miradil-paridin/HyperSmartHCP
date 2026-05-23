<template>
  <article class="metric-card">
    <div class="flex min-w-0 items-start justify-between gap-3">
      <div>
        <div class="text-xs font-bold tracking-[0.12em] text-slate-500">{{ label }}</div>
        <div class="mt-1 whitespace-nowrap text-[28px] font-black leading-none text-white">{{ value }}</div>
      </div>
      <span class="rounded-full border px-2 py-1 text-[10px] font-bold" :class="pillClass">{{ sourceLabel }}</span>
    </div>
    <div class="mt-1 flex items-center justify-between gap-3 text-xs">
      <span class="text-slate-500">{{ range }}</span>
      <span class="font-bold" :class="changeClass">{{ changeLabel }}</span>
    </div>
    <div class="mt-3 min-h-0 flex-1 overflow-hidden rounded-xl bg-black/12 px-2 py-2">
      <svg v-if="linePath" viewBox="0 0 240 86" class="h-full w-full">
        <defs>
          <linearGradient :id="`${id}-line`" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" :stop-color="lineStart" />
            <stop offset="100%" :stop-color="lineEnd" />
          </linearGradient>
          <linearGradient :id="`${id}-fill`" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" :stop-color="fillStart" stop-opacity="0.34" />
            <stop offset="100%" :stop-color="fillEnd" stop-opacity="0" />
          </linearGradient>
        </defs>
        <path d="M 0 16 H 240 M 0 43 H 240 M 0 70 H 240" fill="none" stroke="rgba(148,163,184,0.12)" stroke-width="1" />
        <path :d="fillPath" :fill="`url(#${id}-fill)`" />
        <path :d="linePath" fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" :stroke="`url(#${id}-line)`" />
      </svg>
      <div v-else class="flex h-full items-center justify-center text-xs font-bold text-slate-600">暂无趋势数据</div>
    </div>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  id: string;
  label: string;
  value: string;
  range: string;
  sourceLabel: string;
  pillClass: string;
  lineStart: string;
  lineEnd: string;
  fillStart: string;
  fillEnd: string;
  linePath: string;
  fillPath: string;
  changeLabel: string;
  changeClass: string;
}>();
</script>
