<template>
  <section class="glass-panel tech-border rounded-lg p-4">
    <div class="mb-4 flex items-center justify-between">
      <h2 class="section-title">快捷操作</h2>
      <span class="rounded border border-cyan/20 bg-cyan/10 px-2 py-1 text-xs text-cyan">安全控制</span>
    </div>
    <div class="grid grid-cols-2 gap-3">
      <button
        v-for="action in actions"
        :key="action.id"
        class="flex h-12 items-center gap-2 rounded border border-white/10 bg-white/[0.035] px-3 text-sm font-semibold text-slate-100 transition hover:border-cyan/50 hover:bg-cyan/10 disabled:cursor-not-allowed disabled:opacity-45"
        :disabled="loading === action.id"
        :title="action.label"
        @click="execute(action.id)"
      >
        <component :is="action.icon" class="h-4 w-4 shrink-0" :class="action.color" />
        <span class="truncate">{{ action.label }}</span>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Fan, Lightbulb, LightbulbOff, Power, SunMedium, VenetianMask } from "@lucide/vue";
import { api } from "../services/api";

const emit = defineEmits<{ executed: [message: string] }>();

const loading = ref<string | null>(null);

const actions = [
  { id: "all_lights_on", label: "全屋开灯", icon: Lightbulb, color: "text-cyan" },
  { id: "all_lights_off", label: "全屋关灯", icon: LightbulbOff, color: "text-rose-300" },
  { id: "all_fans_off", label: "关闭风扇", icon: Fan, color: "text-sky-300" },
  { id: "climate_off", label: "关闭空调", icon: Power, color: "text-violet" },
  { id: "curtains_open", label: "打开窗帘", icon: SunMedium, color: "text-amber-300" },
  { id: "curtains_close", label: "关闭窗帘", icon: VenetianMask, color: "text-emerald-300" },
];

async function execute(actionId: string) {
  loading.value = actionId;
  try {
    const result = await api.executeAction(actionId);
    emit("executed", result.message);
  } catch (error) {
    emit("executed", error instanceof Error ? error.message : "控制请求失败");
  } finally {
    loading.value = null;
  }
}
</script>
