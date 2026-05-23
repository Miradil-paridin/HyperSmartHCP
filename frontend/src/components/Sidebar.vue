<template>
  <aside class="glass-panel tech-border flex min-h-0 flex-col rounded-xl p-4">
    <div class="mb-4 flex items-center justify-between">
      <div>
        <div class="section-kicker">总览筛选</div>
        <h2 class="mt-1 text-lg font-bold text-white">设备视角</h2>
      </div>
      <SlidersHorizontal class="h-5 w-5 text-sky-300" />
    </div>

    <div class="min-h-0 flex-1 overflow-y-auto pr-1 thin-scrollbar">
      <section>
        <div class="mb-2 text-xs font-bold tracking-[0.14em] text-slate-500">设备分类</div>
        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="category in categories"
            :key="category.id"
            class="filter-button"
            :class="category.id === selectedCategory ? 'filter-button-active' : ''"
            @click="$emit('update:selectedCategory', category.id)"
          >
            <span class="truncate">{{ category.label }}</span>
            <span class="filter-count">{{ category.count }}</span>
          </button>
        </div>
      </section>

      <section class="mt-5">
        <div class="mb-2 text-xs font-bold tracking-[0.14em] text-slate-500">房间筛选</div>
        <div class="grid grid-cols-2 gap-2">
          <button class="filter-button" :class="selectedRoom === 'all' ? 'filter-button-active' : ''" @click="$emit('update:selectedRoom', 'all')">
            <span class="truncate">全部区域</span>
          </button>
          <button
            v-for="room in rooms"
            :key="room"
            class="filter-button"
            :class="room === selectedRoom ? 'filter-button-active' : ''"
            @click="$emit('update:selectedRoom', room)"
          >
            <span class="truncate">{{ room }}</span>
          </button>
        </div>
      </section>

      <section class="mt-5">
        <div class="mb-2 text-xs font-bold tracking-[0.14em] text-slate-500">状态筛选</div>
        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="status in statusItems"
            :key="status.id"
            class="filter-button"
            :class="status.id === selectedStatus ? 'filter-button-active' : ''"
            @click="$emit('update:selectedStatus', status.id)"
          >
            <span class="h-2 w-2 shrink-0 rounded-full" :class="status.dot" />
            <span class="truncate">{{ status.label }}</span>
          </button>
        </div>
      </section>
    </div>

    <section class="mt-4 shrink-0 rounded-xl border border-sky-300/10 bg-slate-950/28 p-3">
      <div class="flex items-end justify-between">
        <div>
          <div class="text-xs text-slate-500">筛选结果</div>
          <div class="mt-1 text-2xl font-black text-white">{{ filteredCount }}</div>
        </div>
        <div class="text-right text-xs leading-5 text-slate-500">
          <div><span class="text-emerald-200">{{ onlineCount }}</span> 在线</div>
          <div><span class="text-rose-200">{{ abnormalCount }}</span> 异常</div>
        </div>
      </div>
    </section>
  </aside>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { SlidersHorizontal } from "@lucide/vue";
import type { Device, DeviceCategory } from "../types/api";
import type { StatusFilter } from "../composables/useHomeInsights";

const props = defineProps<{
  categories: DeviceCategory[];
  rooms: string[];
  devices: Device[];
  selectedCategory: string;
  selectedRoom: string;
  selectedStatus: StatusFilter;
  filteredCount: number;
}>();

defineEmits<{
  "update:selectedCategory": [value: string];
  "update:selectedRoom": [value: string];
  "update:selectedStatus": [value: StatusFilter];
}>();

const statusItems: { id: StatusFilter; label: string; dot: string }[] = [
  { id: "all", label: "全部", dot: "bg-sky-300" },
  { id: "online", label: "在线", dot: "bg-emerald-300" },
  { id: "abnormal", label: "异常", dot: "bg-amber-300" },
  { id: "offline", label: "离线", dot: "bg-rose-400" },
];

const onlineCount = computed(() => props.devices.filter((device) => device.status === "online").length);
const abnormalCount = computed(() => props.devices.filter((device) => ["offline", "warning", "unknown"].includes(device.status)).length);
</script>
