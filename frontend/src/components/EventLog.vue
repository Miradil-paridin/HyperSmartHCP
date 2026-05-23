<template>
  <section class="glass-panel flex min-h-0 flex-col rounded-xl p-4">
    <div class="mb-3 flex items-center justify-between">
      <div>
        <div class="section-kicker">高价值事件</div>
        <h2 class="mt-1 text-lg font-bold text-white">告警 / 日志</h2>
      </div>
      <ListChecks class="h-5 w-5 text-sky-300" />
    </div>

    <div class="min-h-0 flex-1 overflow-y-auto pr-1 thin-scrollbar">
      <article v-for="event in priorityEvents" :key="event.id" class="event-card">
        <div class="flex items-center justify-between gap-3">
          <span class="rounded-full border px-2 py-0.5 text-[10px] font-black" :class="typeClass(event.type)">{{ event.type }}</span>
          <span class="text-[11px] text-slate-500">{{ formatTime(event.timestamp) }}</span>
        </div>
        <p class="mt-2 truncate text-sm text-slate-200" :title="event.message">{{ readableEvent(event.message) }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { ListChecks } from "@lucide/vue";
import { readableEvent } from "../composables/useHomeInsights";
import type { EventItem } from "../types/api";

const props = defineProps<{ events: EventItem[] }>();

const priorityEvents = computed(() => {
  const score = (type: EventItem["type"]) => ({ ERROR: 0, WARN: 1, AUTO: 2, DEVICE: 3, INFO: 4 })[type] ?? 5;
  return [...props.events].sort((a, b) => score(a.type) - score(b.type)).slice(0, 6);
});

function typeClass(type: EventItem["type"]) {
  return {
    ERROR: "border-rose-300/24 bg-rose-400/10 text-rose-200",
    WARN: "border-amber-300/24 bg-amber-400/10 text-amber-200",
    AUTO: "border-violet-300/24 bg-violet-400/10 text-violet-200",
    DEVICE: "border-teal-300/24 bg-teal-400/10 text-teal-200",
    INFO: "border-sky-300/24 bg-sky-400/10 text-sky-200",
  }[type];
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" }).format(new Date(value));
}
</script>
