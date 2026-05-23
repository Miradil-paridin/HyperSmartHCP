<template>
  <article class="kpi-card">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <div class="text-xs font-bold tracking-[0.16em] text-slate-500">{{ label }}</div>
        <div class="mt-2 flex items-end gap-1.5">
          <strong class="text-[34px] font-black leading-none text-white">{{ value }}</strong>
          <span class="pb-1 text-xs font-semibold text-slate-500">{{ unit }}</span>
        </div>
      </div>
      <div class="relative flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-sky-300/14 bg-slate-950/42">
        <svg v-if="progress !== undefined" viewBox="0 0 48 48" class="absolute inset-0 h-full w-full -rotate-90">
          <circle cx="24" cy="24" r="20" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="4" />
          <circle
            cx="24"
            cy="24"
            r="20"
            fill="none"
            :stroke="accent"
            stroke-linecap="round"
            stroke-width="4"
            :stroke-dasharray="`${safeProgress * 1.256} 126`"
          />
        </svg>
        <component :is="icon" class="h-5 w-5" :style="{ color: accent }" />
      </div>
    </div>
    <p class="mt-2 line-clamp-2 text-sm leading-5 text-slate-400">{{ caption }}</p>
    <div v-if="progress !== undefined" class="mt-3 h-1.5 overflow-hidden rounded-full bg-white/6">
      <div class="h-full rounded-full" :style="{ width: `${safeProgress}%`, backgroundColor: accent }" />
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Component } from "vue";

const props = defineProps<{
  label: string;
  value: number | string;
  unit: string;
  caption: string;
  icon: Component;
  accent: string;
  progress?: number;
}>();

const safeProgress = computed(() => Math.max(0, Math.min(100, props.progress ?? 0)));
</script>
