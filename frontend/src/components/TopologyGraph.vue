<template>
  <section class="glass-panel tech-border relative min-h-0 overflow-hidden rounded-xl p-4">
    <div class="absolute inset-x-4 top-4 z-20 flex items-start justify-between gap-4">
      <div>
        <div class="section-kicker">网络拓扑</div>
        <h2 class="mt-1 text-lg font-bold text-white">实时设备网络</h2>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <span v-if="deviceUpdate" class="panel-chip">{{ shortId(deviceUpdate.id) }} · {{ statusText(deviceUpdate.status) }}</span>
        <span class="panel-chip">在线 {{ statusCounts.online }}</span>
        <span class="panel-chip">离线 {{ statusCounts.offline }}</span>
        <span class="panel-chip">告警 {{ statusCounts.warning }}</span>
      </div>
    </div>

    <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(56,189,248,0.22),transparent_24%),radial-gradient(circle_at_center,rgba(139,109,255,0.12),transparent_50%)]" />
    <div class="pointer-events-none absolute left-1/2 top-1/2 h-[318px] w-[318px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-sky-300/14" />
    <div class="pointer-events-none absolute left-1/2 top-1/2 h-[238px] w-[238px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-dashed border-sky-300/22 shadow-[0_0_70px_rgba(57,200,255,0.18)]" />
    <div class="pointer-events-none absolute left-1/2 top-1/2 h-[158px] w-[158px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-violet-300/28 shadow-[0_0_64px_rgba(139,109,255,0.18)]" />

    <div class="absolute left-1/2 top-1/2 z-10 h-[126px] w-[126px] -translate-x-1/2 -translate-y-1/2">
      <div class="absolute inset-0 rounded-full bg-[conic-gradient(from_120deg,rgba(57,200,255,0.12),rgba(57,200,255,0.82),rgba(139,109,255,0.24),rgba(57,200,255,0.12))] p-px shadow-[0_0_70px_rgba(57,200,255,0.34)]">
        <div class="h-full w-full rounded-full bg-slate-950/88" />
      </div>
      <div class="absolute inset-[12px] rounded-[28px] border border-sky-300/30 bg-[linear-gradient(145deg,rgba(16,33,72,0.98),rgba(7,13,33,0.98))] shadow-[inset_0_0_28px_rgba(57,200,255,0.20)]" />
      <div class="absolute inset-[28px] grid grid-cols-3 gap-1.5 rounded-2xl border border-white/10 bg-sky-400/8 p-2">
        <span v-for="index in 9" :key="index" class="rounded-[5px] border border-sky-200/18 bg-[linear-gradient(145deg,rgba(57,200,255,0.52),rgba(139,109,255,0.22))] shadow-[0_0_14px_rgba(57,200,255,0.25)]" />
      </div>
      <div class="absolute left-1/2 top-1/2 flex h-10 w-10 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-xl border border-white/18 bg-black/28">
        <Network class="h-5 w-5 text-white" />
      </div>
      <div class="pointer-events-none absolute -inset-3 rounded-full border border-sky-300/16 [clip-path:polygon(0_0,100%_0,100%_44%,0_56%)]" />
      <div class="pointer-events-none absolute left-1/2 top-0 h-full w-px -translate-x-1/2 bg-gradient-to-b from-transparent via-sky-200/35 to-transparent" />
    </div>

    <div class="absolute inset-0 z-10">
      <svg viewBox="0 0 900 430" class="h-full w-full" preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="linkGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#39c8ff" stop-opacity="0.15" />
            <stop offset="50%" stop-color="#39c8ff" stop-opacity="0.7" />
            <stop offset="100%" stop-color="#8b6dff" stop-opacity="0.22" />
          </linearGradient>
        </defs>
        <g v-for="node in displayNodes" :key="`line-${node.id}`">
          <line x1="450" y1="215" :x2="node.x" :y2="node.y" stroke="url(#linkGradient)" stroke-width="1.4" stroke-dasharray="6 7" />
          <circle :cx="node.x" :cy="node.y" r="2.5" :fill="node.color" opacity="0.9" />
        </g>
      </svg>
    </div>

    <div class="absolute inset-0 z-20">
      <article
        v-for="node in displayNodes"
        :key="node.id"
        class="absolute w-[176px] rounded-xl border bg-[linear-gradient(180deg,rgba(12,20,45,0.94),rgba(7,12,28,0.94))] px-3 py-2 shadow-[0_16px_40px_rgba(0,0,0,0.28)]"
        :class="node.border"
        :style="{ left: `${node.cardX}%`, top: `${node.cardY}%`, transform: 'translate(-50%, -50%)' }"
      >
        <div class="flex items-center gap-2">
          <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-white/10 bg-black/20">
            <component :is="node.icon" class="h-4.5 w-4.5" :style="{ color: node.color }" />
          </span>
          <div class="min-w-0">
            <div class="truncate text-sm font-bold text-white">{{ node.label }}</div>
            <div class="mt-0.5 text-[11px]" :style="{ color: node.color }">{{ node.statusLabel }}</div>
          </div>
        </div>
        <div class="mt-2 truncate font-mono text-[10px] uppercase tracking-[0.12em] text-slate-500">{{ node.id }}</div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Binary, CircleAlert, Cpu, Lightbulb, Lock, Network, Plug, RadioTower, Thermometer, Waves } from "@lucide/vue";
import type { Component } from "vue";
import type { Device, Topology, TopologyNode } from "../types/api";

const props = defineProps<{
  topology: Topology;
  deviceUpdate?: { id: string; status: Device["status"] } | null;
}>();

type DisplayNode = {
  id: string;
  label: string;
  statusLabel: string;
  color: string;
  border: string;
  icon: Component;
  x: number;
  y: number;
  cardX: number;
  cardY: number;
};

const slots = [
  { x: 254, y: 118, cardX: 24, cardY: 27 },
  { x: 646, y: 118, cardX: 76, cardY: 27 },
  { x: 240, y: 310, cardX: 23, cardY: 72 },
  { x: 660, y: 310, cardX: 77, cardY: 72 },
  { x: 450, y: 352, cardX: 50, cardY: 81 },
  { x: 450, y: 80, cardX: 50, cardY: 18 },
  { x: 310, y: 214, cardX: 31, cardY: 50 },
  { x: 590, y: 214, cardX: 69, cardY: 50 },
];

const displayNodes = computed<DisplayNode[]>(() => {
  const important = props.topology.nodes
    .filter((node) => node.type === "device" && node.category !== "unknown")
    .sort(sortNodes)
    .slice(0, slots.length);

  return important.map((node, index) => {
    const visual = visualFor(node);
    return {
      id: node.id,
      label: node.label,
      statusLabel: statusText(node.status),
      color: visual.color,
      border: visual.border,
      icon: visual.icon,
      ...slots[index],
    };
  });
});

const statusCounts = computed(() => {
  const devices = props.topology.nodes.filter((node) => node.type === "device");
  return {
    online: devices.filter((node) => node.status === "online").length,
    offline: devices.filter((node) => node.status === "offline").length,
    warning: devices.filter((node) => node.status === "warning").length,
  };
});

function sortNodes(a: TopologyNode, b: TopologyNode) {
  const score = (node: TopologyNode) => {
    if (node.status === "warning") return 0;
    if (node.status === "online" && node.category === "light") return 1;
    if (node.status === "online" && node.category === "climate") return 2;
    if (node.status === "online" && ["plug", "curtain", "vacuum", "security", "lock"].includes(node.category ?? "")) return 3;
    if (node.status === "online") return 4;
    if (node.status === "offline") return 5;
    return 6;
  };
  return score(a) - score(b);
}

function visualFor(node: TopologyNode) {
  if (node.status === "offline") {
    return { color: "#ff5c88", border: "border-rose-300/28", icon: CircleAlert };
  }
  if (node.status === "warning") {
    return { color: "#ffb347", border: "border-amber-300/28", icon: CircleAlert };
  }
  if (node.category === "light") return { color: "#39c8ff", border: "border-sky-300/28", icon: Lightbulb };
  if (node.category === "climate") return { color: "#34e0c7", border: "border-teal-300/28", icon: Thermometer };
  if (node.category === "plug") return { color: "#ffb347", border: "border-amber-300/28", icon: Plug };
  if (node.category === "curtain") return { color: "#8b6dff", border: "border-violet-300/28", icon: Waves };
  if (node.category === "lock") return { color: "#ff5c88", border: "border-rose-300/28", icon: Lock };
  if (node.category === "sensor") return { color: "#39c8ff", border: "border-sky-300/28", icon: RadioTower };
  if (node.category === "security") return { color: "#ffb347", border: "border-amber-300/28", icon: Binary };
  return { color: "#9fb3df", border: "border-slate-300/18", icon: Cpu };
}

function shortId(id: string) {
  return id.length <= 28 ? id : `${id.slice(0, 14)}...${id.slice(-10)}`;
}

function statusText(status: Device["status"]) {
  return {
    online: "在线",
    offline: "离线",
    warning: "告警",
    unknown: "未知",
  }[status];
}
</script>
