<template>
  <section class="glass-panel tech-border min-h-0 rounded-lg p-4">
    <div class="mb-4 flex items-center justify-between">
      <h2 class="section-title">消息日志</h2>
      <ListChecks class="h-5 w-5 text-cyan" />
    </div>
    <div class="min-h-0 space-y-2 overflow-y-auto pr-1 thin-scrollbar">
      <article v-for="event in events" :key="event.id" class="rounded border border-white/5 bg-slate-950/30 p-3">
        <div class="mb-2 flex items-center justify-between gap-2">
          <span class="rounded px-2 py-0.5 text-[11px] font-black" :class="tagClass(event.type)">{{ event.type }}</span>
          <time class="text-[11px] text-slate-500">{{ formatTime(event.timestamp) }}</time>
        </div>
        <p class="text-sm leading-5 text-slate-200">{{ event.message }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ListChecks } from "@lucide/vue";
import type { EventItem } from "../types/api";

defineProps<{ events: EventItem[] }>();

function tagClass(type: EventItem["type"]) {
  return {
    INFO: "bg-sky-400/15 text-sky-200",
    WARN: "bg-amber-400/15 text-amber-200",
    ERROR: "bg-rose-400/15 text-rose-200",
    DEVICE: "bg-cyan/15 text-cyan",
    AUTO: "bg-violet/15 text-violet",
  }[type];
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(value));
}
</script>
