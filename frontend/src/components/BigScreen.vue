<template>
  <main class="bigscreen-page" @mouseenter="paused = true" @mouseleave="paused = false">
    <div class="grid min-h-0 min-w-0 grid-rows-[72px_132px_minmax(0,1fr)_220px] gap-4">
      <header class="bigscreen-header">
        <div>
          <div class="section-kicker">HyperLink Home</div>
          <h1 class="mt-1 text-3xl font-black text-white">全屋可视化态势屏</h1>
        </div>
        <div class="flex items-center gap-3">
          <button class="rounded-full border border-sky-300/16 bg-slate-950/38 px-4 py-2 text-sm font-bold text-slate-300" @click="$emit('update:activePage', 'console')">
            返回控制台
          </button>
          <button class="rounded-full border border-sky-300/16 bg-slate-950/38 px-4 py-2 text-sm font-bold text-slate-300" @click="paused = !paused">
            {{ paused ? "继续轮播" : "暂停轮播" }}
          </button>
          <div class="panel-chip">{{ apiMode === "home_assistant" ? "HA 接入" : apiMode.toUpperCase() }}</div>
          <div class="panel-chip">
            <span class="h-2 w-2 rounded-full" :class="connected ? 'bg-emerald-300' : 'bg-rose-400'" />
            {{ connected ? "在线" : "离线" }}
          </div>
          <div class="text-3xl font-black text-white">{{ now }}</div>
        </div>
      </header>

      <section class="grid min-h-0 min-w-0 grid-cols-4 gap-4 overflow-hidden">
        <article v-for="item in kpis" :key="item.label" class="bigscreen-kpi">
          <div class="text-sm tracking-[0.14em] text-slate-500">{{ item.label }}</div>
          <div class="mt-2 text-4xl font-black text-white">{{ item.value }}<span class="ml-1 text-base text-slate-500">{{ item.unit }}</span></div>
          <div class="mt-3 h-1.5 overflow-hidden rounded-full bg-white/6">
            <div class="h-full rounded-full" :class="item.bar" :style="{ width: item.progress }" />
          </div>
        </article>
      </section>

      <section class="grid min-h-0 min-w-0 grid-cols-[320px_minmax(0,1fr)_380px] gap-4 overflow-hidden">
        <aside class="bigscreen-panel min-h-0 min-w-0 overflow-hidden rounded-3xl p-6">
          <div class="section-kicker">环境摘要</div>
          <h2 class="mt-2 text-3xl font-black text-white">{{ currentView === "energy" ? "环境能耗" : "全屋环境" }}</h2>
          <div class="mt-6 space-y-4">
            <div v-for="item in envItems" :key="item.label" class="rounded-2xl border border-sky-300/12 bg-slate-950/24 p-4">
              <div class="text-sm text-slate-500">{{ item.label }}</div>
              <div class="mt-2 text-4xl font-black text-white">{{ item.value }}</div>
              <div class="mt-3 h-2 overflow-hidden rounded-full bg-white/6">
                <div class="h-full rounded-full" :class="item.bar" :style="{ width: item.progress }" />
              </div>
            </div>
          </div>
        </aside>

        <BigScreenTopology :groups="screenGroups" :title="viewTitle" :subtitle="viewSubtitle" />

        <aside class="grid min-h-0 min-w-0 grid-rows-[minmax(0,1fr)_180px] gap-4 overflow-hidden">
          <section class="bigscreen-panel flex min-h-0 min-w-0 flex-col overflow-hidden rounded-3xl p-6">
            <div class="mb-5 flex items-center justify-between">
              <div>
                <div class="section-kicker">事件流</div>
                <h2 class="mt-2 text-3xl font-black text-white">{{ currentView === "security" ? "安防告警" : "实时事件" }}</h2>
              </div>
              <div class="rounded-full bg-rose-400/10 px-3 py-1 text-sm font-bold text-rose-200">{{ alertCount }} 异常</div>
            </div>
            <div class="min-h-0 flex-1 overflow-y-auto pr-1 thin-scrollbar">
              <article v-for="event in readableEvents" :key="event.id" class="mb-3 rounded-2xl border border-sky-300/12 bg-slate-950/26 p-4">
                <div class="flex items-center justify-between">
                  <span class="text-sm font-black text-sky-200">{{ event.type }}</span>
                  <span class="text-xs text-slate-500">{{ event.time }}</span>
                </div>
                <p class="mt-2 line-clamp-2 text-lg font-semibold leading-7 text-slate-100">{{ event.message }}</p>
              </article>
            </div>
          </section>
          <section class="bigscreen-panel min-h-0 min-w-0 overflow-hidden rounded-3xl p-5">
            <div class="section-kicker">自动化趋势</div>
            <h2 class="mt-2 text-2xl font-black text-white">执行态势</h2>
            <div class="mt-5 flex h-16 items-end justify-between gap-2 overflow-hidden">
              <span v-for="bar in automationBars" :key="bar.id" class="w-full rounded-t-lg bg-sky-300/70" :style="{ height: `${bar.value}%` }" />
            </div>
            <div class="mt-4 truncate text-sm text-slate-400">{{ enabledAutomationCount }} 条规则启用，轮播视图：{{ viewTitle }}</div>
          </section>
        </aside>
      </section>

      <section class="grid min-h-0 min-w-0 overflow-hidden">
        <MetricCharts v-if="metrics" :metrics="metrics" />
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import BigScreenTopology from "./BigScreenTopology.vue";
import MetricCharts from "./MetricCharts.vue";
import { readableEvent } from "../composables/useHomeInsights";
import type { AutomationRule, EventItem, Metrics, Overview } from "../types/api";
import type { DeviceGroup } from "../composables/useHomeInsights";

const props = defineProps<{
  apiMode: string;
  connected: boolean;
  overview: Overview | null;
  metrics: Metrics | null;
  events: EventItem[];
  automations: AutomationRule[];
  roomSummaries: DeviceGroup[];
  typeSummaries: DeviceGroup[];
}>();

defineEmits<{ "update:activePage": [page: "console" | "screen"] }>();

const views = ["overview", "energy", "security"] as const;
const viewIndex = ref(0);
const paused = ref(false);
const now = ref("");
let clockTimer: number | undefined;
let carouselTimer: number | undefined;

const currentView = computed(() => views[viewIndex.value]);
const screenGroups = computed(() => (props.typeSummaries.length >= 6 ? props.typeSummaries : props.roomSummaries));
const alertCount = computed(() => screenGroups.value.reduce((sum, group) => sum + group.abnormalCount, 0));
const enabledAutomationCount = computed(() => props.automations.filter((rule) => rule.enabled).length);

const viewTitle = computed(() => {
  if (currentView.value === "energy") return "环境能耗态势";
  if (currentView.value === "security") return "安防告警态势";
  return "全屋设备分布";
});

const viewSubtitle = computed(() => {
  if (currentView.value === "energy") return "聚焦环境、光照与功率变化。";
  if (currentView.value === "security") return "优先展示异常、离线与安防相关分组。";
  return "按设备类型形成稳定分组，适合远距离查看全局状态。";
});

const kpis = computed(() => {
  const total = props.overview?.total_devices ?? 0;
  const online = props.overview?.online_devices ?? 0;
  const offline = props.overview?.offline_devices ?? 0;
  const health = props.overview?.home_health ?? 0;
  return [
    { label: "接入实体", value: total, unit: "个", progress: "100%", bar: "bg-sky-300" },
    { label: "在线实体", value: online, unit: "个", progress: `${total ? Math.round((online / total) * 100) : 0}%`, bar: "bg-teal-300" },
    { label: "异常离线", value: offline, unit: "个", progress: `${total ? Math.round((offline / total) * 100) : 0}%`, bar: "bg-rose-400" },
    { label: "健康度", value: health, unit: "%", progress: `${health}%`, bar: "bg-violet-300" },
  ];
});

const envItems = computed(() => [
  { label: "平均温度", value: `${last(props.metrics?.series.temperature)} C`, progress: "62%", bar: "bg-sky-300" },
  { label: "平均湿度", value: `${last(props.metrics?.series.humidity)} %`, progress: "58%", bar: "bg-teal-300" },
  { label: "光照强度", value: `${last(props.metrics?.series.illuminance)} lux`, progress: "54%", bar: "bg-violet-300" },
]);

const readableEvents = computed(() =>
  props.events.slice(0, 3).map((event) => ({
    ...event,
    message: readableEvent(event.message),
    time: new Intl.DateTimeFormat("zh-CN", { hour: "2-digit", minute: "2-digit" }).format(new Date(event.timestamp)),
  })),
);

const automationBars = computed(() =>
  Array.from({ length: 12 }, (_, index) => ({ id: index, value: 22 + ((index * 17 + enabledAutomationCount.value * 13) % 68) })),
);

function tick() {
  now.value = new Intl.DateTimeFormat("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" }).format(new Date());
}

function last(values?: number[]) {
  return values?.length ? values[values.length - 1] : "--";
}

onMounted(() => {
  tick();
  clockTimer = window.setInterval(tick, 1000);
  carouselTimer = window.setInterval(() => {
    if (!paused.value) viewIndex.value = (viewIndex.value + 1) % views.length;
  }, 15000);
});

onUnmounted(() => {
  if (clockTimer) window.clearInterval(clockTimer);
  if (carouselTimer) window.clearInterval(carouselTimer);
});
</script>
