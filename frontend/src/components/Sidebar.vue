<template>
  <aside class="glass-panel tech-border flex min-h-0 flex-col rounded-lg p-4">
    <div class="mb-4 flex items-center justify-between">
      <h2 class="section-title">连接中心</h2>
      <Network class="h-5 w-5 text-cyan" />
    </div>

    <div class="space-y-2">
      <button
        v-for="category in categories"
        :key="category.id"
        class="grid w-full grid-cols-[28px_1fr_auto] items-center rounded border border-white/5 bg-white/[0.025] px-3 py-2.5 text-left transition hover:border-cyan/40 hover:bg-cyan/10"
        :class="category.id === selected ? 'border-cyan/50 bg-cyan/10 shadow-glow' : ''"
        @click="selected = category.id"
      >
        <span class="h-2.5 w-2.5 rounded-full bg-cyan/70 shadow-[0_0_12px_rgba(94,234,212,0.8)]" />
        <span class="text-sm text-slate-200">{{ category.label }}</span>
        <span class="text-xs text-slate-500">{{ category.count }}</span>
      </button>
    </div>

    <div class="mt-5 min-h-0 flex-1 overflow-y-auto pr-1 thin-scrollbar">
      <div v-for="device in filteredDevices" :key="device.id" class="mb-2 rounded border border-white/5 bg-slate-950/30 p-3">
        <div class="flex items-center justify-between gap-3">
          <div class="min-w-0">
            <div class="truncate text-sm font-semibold text-slate-100">{{ device.name }}</div>
            <div class="mt-1 text-xs text-slate-500">{{ device.room }} · {{ device.state }}</div>
          </div>
          <span class="h-2.5 w-2.5 shrink-0 rounded-full" :class="statusClass(device.status)" />
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { Network } from "@lucide/vue";
import type { Device, DeviceCategory } from "../types/api";

const props = defineProps<{
  categories: DeviceCategory[];
  devices: Device[];
}>();

const selected = ref("all");

const filteredDevices = computed(() =>
  selected.value === "all" ? props.devices : props.devices.filter((device) => device.category === selected.value),
);

function statusClass(status: Device["status"]) {
  return {
    online: "bg-emerald-300 shadow-[0_0_12px_#6ee7b7]",
    offline: "bg-rose-400 shadow-[0_0_12px_#fb7185]",
    warning: "bg-amber-300 shadow-[0_0_12px_#fcd34d]",
    unknown: "bg-slate-400",
  }[status];
}
</script>
