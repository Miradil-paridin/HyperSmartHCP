<template>
  <section class="glass-panel flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl p-4">
    <div class="mb-3 flex items-center justify-between">
      <div>
        <div class="section-kicker">实时遥测</div>
        <h2 class="mt-1 text-base font-bold text-white">环境与能耗趋势</h2>
      </div>
      <div class="panel-chip">实时 / 模拟趋势</div>
    </div>

    <div class="grid min-h-0 min-w-0 flex-1 grid-cols-[repeat(4,minmax(0,1fr))] gap-4 overflow-hidden">
      <MetricTrendCard v-for="card in cards" :key="card.id" v-bind="card" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import MetricTrendCard from "./MetricTrendCard.vue";
import type { Metrics } from "../types/api";

const props = defineProps<{ metrics: Metrics }>();

function lastValue(values: number[]) {
  return values.length ? values[values.length - 1] : "--";
}

function buildLinePath(values: number[]) {
  if (!values.length) return "";
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  return values
    .map((value, index) => {
      const x = (index / Math.max(1, values.length - 1)) * 240;
      const y = 68 - ((value - min) / span) * 52;
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

function buildFillPath(values: number[]) {
  const linePath = buildLinePath(values);
  if (!linePath) return "";
  return `${linePath} L 240 82 L 0 82 Z`;
}

const cards = computed(() => [
  card("temperature", "温度", `${lastValue(props.metrics.series.temperature)} C`, "18 - 32 C", props.metrics.series.temperature, "#4dc8ff", "#376dff", "border-sky-400/24 bg-sky-400/10 text-sky-200"),
  card("humidity", "湿度", `${lastValue(props.metrics.series.humidity)} %`, "35 - 75%", props.metrics.series.humidity, "#34e0c7", "#47c3ff", "border-teal-400/24 bg-teal-400/10 text-teal-200"),
  card("illuminance", "光照", `${lastValue(props.metrics.series.illuminance)} lux`, "0 - 1000 lux", props.metrics.series.illuminance, "#a86cff", "#ff6abf", "border-violet-400/24 bg-violet-400/10 text-violet-200"),
  card("power", "功率", `${lastValue(props.metrics.series.power)} W`, "0 - 3000 W", props.metrics.series.power, "#ffb347", "#ff7a3c", "border-orange-400/24 bg-orange-400/10 text-orange-200"),
]);

function card(
  id: string,
  label: string,
  value: string,
  range: string,
  series: number[],
  lineStart: string,
  lineEnd: string,
  pillClass: string,
) {
  return {
    id,
    label,
    value,
    range,
    sourceLabel: series.length >= 12 ? "实时" : "模拟",
    pillClass,
    lineStart,
    lineEnd,
    fillStart: lineStart,
    fillEnd: "#071124",
    linePath: buildLinePath(series),
    fillPath: buildFillPath(series),
  };
}
</script>
