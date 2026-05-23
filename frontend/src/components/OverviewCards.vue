<template>
  <section class="grid min-h-0 grid-cols-4 gap-4">
    <KpiCard
      v-for="card in cards"
      :key="card.label"
      :label="card.label"
      :value="card.value"
      :unit="card.unit"
      :caption="card.caption"
      :icon="card.icon"
      :accent="card.accent"
      :progress="card.progress"
    />
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Cpu, HeartPulse, RadioTower, ShieldAlert } from "@lucide/vue";
import KpiCard from "./KpiCard.vue";
import type { Overview } from "../types/api";

const props = defineProps<{ overview: Overview }>();

function percent(value: number, total: number) {
  return total > 0 ? Math.round((value / total) * 100) : 0;
}

const onlineRate = computed(() => percent(props.overview.online_devices, props.overview.total_devices));
const abnormalCount = computed(() => props.overview.offline_devices);

const cards = computed(() => [
  {
    label: "接入设备 / 实体",
    value: props.overview.total_devices,
    unit: "个",
    caption: "当前纳入 HyperLink Home 总览的 Home Assistant 实体。",
    icon: Cpu,
    accent: "#39c8ff",
    progress: 100,
  },
  {
    label: "在线率",
    value: onlineRate.value,
    unit: "%",
    caption: `基于 Home Assistant 实体状态统计：${props.overview.online_devices} 个可用。`,
    icon: RadioTower,
    accent: "#34e0c7",
    progress: onlineRate.value,
  },
  {
    label: "异常 / 离线",
    value: abnormalCount.value,
    unit: "个",
    caption: "包含 unavailable、unknown 与连接中断实体，建议优先处理常用设备。",
    icon: ShieldAlert,
    accent: "#ff5c88",
    progress: Math.min(100, percent(abnormalCount.value, props.overview.total_devices)),
  },
  {
    label: "系统健康度",
    value: props.overview.home_health,
    unit: "%",
    caption: "综合色在线率、异常数量与后端服务稳定性的总览评分。",
    icon: HeartPulse,
    accent: "#8b6dff",
    progress: props.overview.home_health,
  },
]);
</script>
