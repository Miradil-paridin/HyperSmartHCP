<template>
  <header class="glass-panel tech-border grid grid-cols-[286px_1fr_380px] items-center rounded-xl px-4">
    <div class="flex items-center gap-4">
      <div class="flex h-12 w-12 items-center justify-center rounded-xl border border-sky-400/24 bg-sky-500/10">
        <div class="grid h-7 w-7 grid-cols-3 gap-1">
          <span v-for="n in 9" :key="n" class="rounded-[2px] bg-gradient-to-br from-sky-300 to-blue-600" />
        </div>
      </div>
      <div>
        <div class="section-kicker">HyperLink Home</div>
        <h1 class="mt-1 text-[26px] font-[800] leading-none text-white">智能中控台</h1>
        <p class="mt-1 text-[11px] text-slate-500">Home Assistant 家庭设备联动控制层</p>
      </div>
    </div>

    <nav class="mx-6 flex h-full items-center gap-2 overflow-hidden">
      <button
        v-for="item in navItems"
        :key="item.id"
        class="whitespace-nowrap rounded-lg border px-4 py-2 text-sm font-semibold transition"
        :class="
          item.id === activePage
            ? 'border-sky-400/36 bg-sky-500/12 text-white'
            : 'border-transparent text-slate-400 hover:border-white/8 hover:bg-white/[0.03] hover:text-slate-200'
        "
        @click="$emit('update:activePage', item.id)"
      >
        {{ item.label }}
      </button>
    </nav>

    <div class="flex items-center justify-end gap-2">
      <div class="flex min-w-0 max-w-[150px] items-center gap-2 rounded-full border border-white/10 bg-slate-950/50 px-3 py-2 text-sm text-slate-500">
        <Search class="h-4 w-4 text-slate-500" />
        <span class="truncate">搜索设备</span>
      </div>

      <div class="panel-chip">
        <span class="h-2 w-2 rounded-full" :class="connected ? 'bg-emerald-300 shadow-[0_0_12px_#6ee7b7]' : 'bg-rose-400'" />
        <span>{{ connected ? "在线" : "离线" }}</span>
      </div>

      <div class="panel-chip">
        <Cpu class="h-3.5 w-3.5 text-sky-300" />
        <span>{{ apiMode === "home_assistant" ? "HA 接入" : apiMode.toUpperCase() }}</span>
      </div>

      <div class="rounded-lg border border-white/10 bg-slate-950/40 px-3 py-2 text-xs text-slate-300">
        {{ currentTime }}
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { Cpu, Search } from "@lucide/vue";

defineProps<{
  apiMode: string;
  connected: boolean;
  activePage: "console" | "screen";
}>();

defineEmits<{ "update:activePage": [page: "console" | "screen"] }>();

const currentTime = ref("");
const navItems: { id: "console" | "screen"; label: string }[] = [
  { id: "console", label: "控制台" },
  { id: "screen", label: "可视化大屏" },
];
let timer: number | undefined;

function tick() {
  currentTime.value = new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
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
