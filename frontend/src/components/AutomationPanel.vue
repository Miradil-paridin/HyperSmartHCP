<template>
  <section class="glass-panel tech-border min-h-0 rounded-lg p-4">
    <div class="mb-3 flex items-center justify-between">
      <h2 class="section-title">自动化规则</h2>
      <Workflow class="h-5 w-5 text-violet" />
    </div>
    <div class="space-y-2">
      <article v-for="rule in rules" :key="rule.id" class="rounded border border-white/5 bg-slate-950/30 p-3">
        <div class="flex items-center justify-between gap-2">
          <h3 class="truncate text-sm font-bold text-slate-100">{{ rule.name }}</h3>
          <span class="rounded px-2 py-0.5 text-[11px]" :class="rule.enabled ? 'bg-emerald-300/15 text-emerald-200' : 'bg-slate-500/15 text-slate-400'">
            {{ rule.enabled ? "ON" : "OFF" }}
          </span>
        </div>
        <p class="mt-2 truncate text-xs text-slate-500">{{ rule.trigger }}</p>
        <p class="mt-1 truncate text-xs text-cyan/80">{{ rule.action }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { Workflow } from "@lucide/vue";
import type { AutomationRule } from "../types/api";

defineProps<{ rules: AutomationRule[] }>();
</script>
