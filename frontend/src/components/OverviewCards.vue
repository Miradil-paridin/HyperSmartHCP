<template>
  <section class="grid grid-cols-5 gap-4">
    <article v-for="card in cards" :key="card.label" class="glass-panel tech-border rounded-lg px-5 py-4">
      <div class="flex items-center justify-between">
        <span class="text-sm text-slate-400">{{ card.label }}</span>
        <component :is="card.icon" class="h-5 w-5" :class="card.color" />
      </div>
      <div class="mt-3 flex items-end gap-2">
        <strong class="text-3xl font-black text-white">{{ card.value }}</strong>
        <span class="pb-1 text-xs text-slate-500">{{ card.unit }}</span>
      </div>
      <div class="mt-3 h-1 overflow-hidden rounded-full bg-white/10">
        <div class="h-full rounded-full" :class="card.bar" :style="{ width: card.progress }" />
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Activity, Cpu, HeartPulse, RadioTower, ShieldAlert } from "@lucide/vue";
import type { Overview } from "../types/api";

const props = defineProps<{ overview: Overview }>();

const cards = computed(() => [
  {
    label: "总设备数",
    value: props.overview.total_devices,
    unit: "devices",
    icon: Cpu,
    color: "text-cyan",
    bar: "bg-cyan",
    progress: "100%",
  },
  {
    label: "在线设备",
    value: props.overview.online_devices,
    unit: "online",
    icon: RadioTower,
    color: "text-emerald-300",
    bar: "bg-emerald-300",
    progress: `${(props.overview.online_devices / props.overview.total_devices) * 100}%`,
  },
  {
    label: "离线设备",
    value: props.overview.offline_devices,
    unit: "offline",
    icon: ShieldAlert,
    color: "text-rose-300",
    bar: "bg-rose-300",
    progress: `${(props.overview.offline_devices / props.overview.total_devices) * 100}%`,
  },
  {
    label: "今日事件",
    value: props.overview.today_events,
    unit: "events",
    icon: Activity,
    color: "text-amber-300",
    bar: "bg-amber-300",
    progress: "78%",
  },
  {
    label: "家庭健康度",
    value: props.overview.home_health,
    unit: "%",
    icon: HeartPulse,
    color: "text-violet",
    bar: "bg-violet",
    progress: `${props.overview.home_health}%`,
  },
]);
</script>
