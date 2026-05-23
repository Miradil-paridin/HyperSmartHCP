<template>
  <section class="glass-panel tech-border flex min-h-0 flex-col rounded-xl p-5">
    <div class="mb-4 flex items-start justify-between gap-4">
      <div>
        <div class="section-kicker">主视图</div>
        <h2 class="mt-1 text-xl font-black text-white">{{ mode === "room" ? "全屋空间关系图" : "设备类型拓扑" }}</h2>
        <p class="mt-1 text-sm text-slate-500">中心节点连接分组与代表设备，点击分组后查看右侧详情。</p>
      </div>
      <div class="flex rounded-xl border border-sky-300/14 bg-slate-950/35 p-1">
        <button
          v-for="item in modes"
          :key="item.id"
          class="rounded-lg px-3 py-1.5 text-xs font-bold transition"
          :class="mode === item.id ? 'bg-sky-500/16 text-white' : 'text-slate-500 hover:text-slate-300'"
          @click="$emit('update:mode', item.id)"
        >
          {{ item.label }}
        </button>
      </div>
    </div>

    <div class="topology-stage">
      <svg class="absolute inset-0 h-full w-full" viewBox="0 0 900 460" preserveAspectRatio="none">
        <defs>
          <linearGradient id="consoleLink" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#39c8ff" stop-opacity="0.15" />
            <stop offset="50%" stop-color="#39c8ff" stop-opacity="0.48" />
            <stop offset="100%" stop-color="#34e0c7" stop-opacity="0.12" />
          </linearGradient>
        </defs>
        <line
          v-for="node in positionedGroups"
          :key="`line-${node.id}`"
          x1="450"
          y1="230"
          :x2="node.svgX"
          :y2="node.svgY"
          stroke="url(#consoleLink)"
          stroke-width="1.4"
          stroke-dasharray="8 10"
        />
      </svg>

      <div class="topology-core">
        <div class="text-[11px] font-bold tracking-[0.18em] text-sky-300">HYPERLINK</div>
        <div class="mt-1 text-2xl font-black text-white">{{ totalDevices }}</div>
        <div class="mt-1 text-xs text-slate-500">实体总览</div>
        <div class="mt-4 grid grid-cols-2 gap-2 text-center text-xs">
          <div class="rounded-lg bg-emerald-400/8 px-2 py-1.5 text-emerald-200">{{ onlineDevices }} 在线</div>
          <div class="rounded-lg bg-rose-400/8 px-2 py-1.5 text-rose-200">{{ abnormalDevices }} 异常</div>
        </div>
      </div>

      <button
        v-for="node in positionedGroups"
        :key="node.id"
        class="topology-node"
        :class="[selectedId === node.id ? 'topology-node-active' : '', node.abnormalCount ? 'topology-node-warn' : '']"
        :style="{ left: `${node.x}%`, top: `${node.y}%` }"
        @click="$emit('select', { type: node.kind, id: node.id })"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <div class="truncate text-base font-black text-white" :title="node.name">{{ node.name }}</div>
            <div class="mt-1 text-xs text-slate-500">{{ node.deviceCount }} 个实体 · {{ node.onlineCount }} 在线</div>
          </div>
          <span class="topology-status" :class="node.abnormalCount ? 'bg-rose-400/16 text-rose-200' : 'bg-emerald-400/12 text-emerald-200'">
            {{ node.abnormalCount ? `${node.abnormalCount} 异常` : "正常" }}
          </span>
        </div>
        <div class="mt-3 flex flex-wrap gap-1.5">
          <span v-for="device in node.devices.slice(0, 3)" :key="device.id" class="device-dot" :class="dotClass(device.status)" :title="`${device.name} · ${device.id}`" />
          <span v-if="node.deviceCount > 3" class="text-[10px] text-slate-500">+{{ node.deviceCount - 3 }}</span>
        </div>
        <div class="mt-3 h-1.5 overflow-hidden rounded-full bg-white/6">
          <div class="h-full rounded-full bg-sky-300" :style="{ width: onlinePercent(node.onlineCount, node.deviceCount) }" />
        </div>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Device } from "../types/api";
import type { DeviceGroup, TopologyMode } from "../composables/useHomeInsights";

const props = defineProps<{
  mode: TopologyMode;
  roomSummaries: DeviceGroup[];
  typeSummaries: DeviceGroup[];
  selectedId: string | null;
}>();

defineEmits<{
  "update:mode": [mode: TopologyMode];
  select: [selection: { type: TopologyMode; id: string }];
}>();

type PositionedGroup = DeviceGroup & { x: number; y: number; svgX: number; svgY: number };

const modes: { id: TopologyMode; label: string }[] = [
  { id: "room", label: "按房间" },
  { id: "type", label: "按设备类型" },
];

const groups = computed(() => (props.mode === "room" ? props.roomSummaries : props.typeSummaries).slice(0, 8));

const totalDevices = computed(() => groups.value.reduce((sum, group) => sum + group.deviceCount, 0));
const onlineDevices = computed(() => groups.value.reduce((sum, group) => sum + group.onlineCount, 0));
const abnormalDevices = computed(() => groups.value.reduce((sum, group) => sum + group.abnormalCount, 0));

const positionedGroups = computed<PositionedGroup[]>(() => {
  const slots = [
    { x: 20, y: 20 },
    { x: 50, y: 16 },
    { x: 80, y: 20 },
    { x: 18, y: 50 },
    { x: 82, y: 50 },
    { x: 20, y: 80 },
    { x: 50, y: 84 },
    { x: 80, y: 80 },
  ];
  return groups.value.map((group, index) => {
    const slot = slots[index % slots.length];
    return {
      ...group,
      x: slot.x,
      y: slot.y,
      svgX: (slot.x / 100) * 900,
      svgY: (slot.y / 100) * 460,
    };
  });
});

function onlinePercent(online: number, total: number) {
  return `${total > 0 ? Math.round((online / total) * 100) : 0}%`;
}

function dotClass(status: Device["status"]) {
  return {
    online: "bg-emerald-300",
    offline: "bg-rose-400",
    warning: "bg-amber-300",
    unknown: "bg-slate-400",
  }[status];
}
</script>
