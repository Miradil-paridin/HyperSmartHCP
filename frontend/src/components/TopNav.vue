<template>
  <header class="glass-panel tech-border grid grid-cols-[1fr_auto_1fr] items-center rounded-lg px-6">
    <div>
      <div class="text-[11px] font-semibold uppercase text-cyan/70">LAN Intelligence Console</div>
      <h1 class="mt-1 text-2xl font-black text-white">HyperLink Home</h1>
    </div>

    <div class="flex items-center gap-8 text-sm">
      <div class="flex items-center gap-2">
        <span class="h-2.5 w-2.5 rounded-full" :class="connected ? 'bg-emerald-300 shadow-[0_0_14px_#6ee7b7]' : 'bg-rose-400'" />
        <span class="text-slate-200">{{ connected ? "后端在线" : "后端离线" }}</span>
      </div>
      <div class="rounded border border-cyan/20 px-3 py-1.5 text-cyan">{{ apiMode.toUpperCase() }}</div>
      <div class="text-slate-300">{{ currentTime }}</div>
    </div>

    <div class="flex justify-end gap-3 text-xs text-slate-400">
      <div class="rounded border border-white/10 px-3 py-2">NAS Ready</div>
      <div class="rounded border border-white/10 px-3 py-2">HA Bridge</div>
      <div class="rounded border border-white/10 px-3 py-2">v0.1</div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";

defineProps<{
  apiMode: string;
  connected: boolean;
}>();

const currentTime = ref("");
let timer: number | undefined;

function tick() {
  currentTime.value = new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
}

onMounted(() => {
  tick();
  timer = window.setInterval(tick, 1000);
});

onUnmounted(() => {
  if (timer) window.clearInterval(timer);
});
</script>
