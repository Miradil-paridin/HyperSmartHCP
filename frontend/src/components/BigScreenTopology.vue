<template>
  <section class="bigscreen-panel relative min-h-0 overflow-hidden rounded-3xl p-8">
    <div class="relative z-10 flex items-start justify-between">
      <div>
        <div class="section-kicker">全屋态势</div>
        <h2 class="mt-2 text-4xl font-black text-white">{{ title }}</h2>
        <p class="mt-2 text-base text-slate-400">{{ subtitle }}</p>
      </div>
      <div class="rounded-2xl border border-sky-300/16 bg-sky-400/8 px-5 py-3 text-right">
        <div class="text-3xl font-black text-white">{{ totalDevices }}</div>
        <div class="text-xs text-slate-400">纳管实体</div>
      </div>
    </div>

    <div class="absolute left-1/2 top-[60%] h-[270px] w-[270px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-sky-300/12" />
    <div class="absolute left-1/2 top-[60%] h-[460px] w-[460px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-dashed border-sky-300/10" />
    <div class="absolute left-1/2 top-[60%] flex h-32 w-32 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-[32px] border border-sky-300/24 bg-[radial-gradient(circle,rgba(57,200,255,0.22),rgba(7,13,31,0.94)_68%)] shadow-[0_0_80px_rgba(57,200,255,0.18)]">
      <div class="text-center">
        <div class="text-4xl font-black text-white">{{ onlineDevices }}</div>
        <div class="mt-1 text-xs tracking-[0.18em] text-sky-300">ONLINE</div>
      </div>
    </div>

    <svg class="absolute inset-0 h-full w-full" viewBox="0 0 1000 560" preserveAspectRatio="none">
      <g v-for="node in positionedGroups" :key="`big-line-${node.id}`">
        <line x1="500" y1="336" :x2="node.svgX" :y2="node.svgY" stroke="rgba(57,200,255,0.24)" stroke-width="1.5" stroke-dasharray="10 14" />
      </g>
    </svg>

    <button
      v-for="node in positionedGroups"
      :key="node.id"
      class="bigscreen-node"
      :class="node.abnormalCount ? 'bigscreen-node-alert' : ''"
      :style="{ left: `${node.x}%`, top: `${node.y}%` }"
    >
      <div class="flex items-center justify-between gap-4">
        <div class="min-w-0">
          <div class="truncate text-xl font-black text-white">{{ node.name }}</div>
          <div class="mt-1 text-sm text-slate-400">{{ node.deviceCount }} 实体 · {{ node.onlineCount }} 在线</div>
        </div>
        <div class="text-right">
          <div class="text-2xl font-black" :class="node.abnormalCount ? 'text-rose-200' : 'text-emerald-200'">{{ node.abnormalCount }}</div>
          <div class="text-[10px] text-slate-500">异常</div>
        </div>
      </div>
    </button>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { DeviceGroup } from "../composables/useHomeInsights";

const props = defineProps<{
  groups: DeviceGroup[];
  title: string;
  subtitle: string;
}>();

const totalDevices = computed(() => props.groups.reduce((sum, group) => sum + group.deviceCount, 0));
const onlineDevices = computed(() => props.groups.reduce((sum, group) => sum + group.onlineCount, 0));

const positionedGroups = computed(() => {
  const slots = [
    { x: 21, y: 42 },
    { x: 50, y: 34 },
    { x: 79, y: 42 },
    { x: 21, y: 76 },
    { x: 50, y: 84 },
    { x: 79, y: 76 },
  ];
  return props.groups.slice(0, 6).map((group, index) => {
    const slot = slots[index % slots.length];
    return { ...group, ...slot, svgX: slot.x * 10, svgY: slot.y * 5.6 };
  });
});
</script>
