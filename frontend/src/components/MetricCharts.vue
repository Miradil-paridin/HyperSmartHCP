<template>
  <section class="glass-panel tech-border rounded-lg p-4">
    <div class="mb-3 flex items-center justify-between">
      <h2 class="section-title">数据监控</h2>
      <span class="text-xs text-slate-500">2s realtime mock</span>
    </div>
    <div ref="chartEl" class="h-[238px] w-full" />
  </section>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import type { Metrics } from "../types/api";

const props = defineProps<{ metrics: Metrics }>();
const chartEl = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

function renderChart() {
  if (!chartEl.value) return;
  chart ??= echarts.init(chartEl.value, "dark");
  chart.setOption({
    backgroundColor: "transparent",
    color: ["#5eead4", "#60a5fa", "#fcd34d", "#a78bfa"],
    tooltip: { trigger: "axis", backgroundColor: "rgba(2,6,23,0.92)", borderColor: "rgba(94,234,212,0.28)" },
    legend: { top: 0, right: 0, textStyle: { color: "#94a3b8" } },
    grid: { left: 38, right: 22, top: 42, bottom: 28 },
    xAxis: {
      type: "category",
      data: props.metrics.labels,
      axisLine: { lineStyle: { color: "rgba(148,163,184,0.25)" } },
      axisLabel: { color: "#64748b" },
    },
    yAxis: {
      type: "value",
      splitLine: { lineStyle: { color: "rgba(148,163,184,0.12)" } },
      axisLabel: { color: "#64748b" },
    },
    series: [
      { name: "温度", type: "line", smooth: true, data: props.metrics.series.temperature, symbol: "none" },
      { name: "湿度", type: "line", smooth: true, data: props.metrics.series.humidity, symbol: "none" },
      { name: "光照", type: "line", smooth: true, data: props.metrics.series.illuminance, symbol: "none" },
      { name: "功率", type: "line", smooth: true, data: props.metrics.series.power, symbol: "none" },
    ],
  });
}

function resize() {
  chart?.resize();
}

onMounted(() => {
  renderChart();
  window.addEventListener("resize", resize);
});

watch(() => props.metrics, renderChart, { deep: true });

onBeforeUnmount(() => {
  window.removeEventListener("resize", resize);
  chart?.dispose();
});
</script>
