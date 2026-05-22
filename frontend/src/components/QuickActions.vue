<template>
  <section class="glass-panel tech-border rounded-lg p-4">
    <div class="mb-4 flex items-center justify-between">
      <h2 class="section-title">快捷操作</h2>
      <Zap class="h-5 w-5 text-amber-300" />
    </div>
    <div class="grid grid-cols-2 gap-3">
      <button
        v-for="action in actions"
        :key="action.id"
        class="flex h-12 items-center gap-2 rounded border border-white/10 bg-white/[0.035] px-3 text-sm font-semibold text-slate-100 transition hover:border-cyan/50 hover:bg-cyan/10 disabled:cursor-wait disabled:opacity-60"
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
import { Clapperboard, Home, LightbulbOff, Moon, Plane, Sparkles, Zap } from "@lucide/vue";
import { api } from "../services/api";

const emit = defineEmits<{ executed: [message: string] }>();

const loading = ref<string | null>(null);

const actions = [
  { id: "home_mode", label: "回家模式", icon: Home, color: "text-cyan" },
  { id: "away_mode", label: "离家模式", icon: Plane, color: "text-sky-300" },
  { id: "sleep_mode", label: "睡眠模式", icon: Moon, color: "text-violet" },
  { id: "movie_mode", label: "观影模式", icon: Clapperboard, color: "text-amber-300" },
  { id: "all_lights_off", label: "全屋关灯", icon: LightbulbOff, color: "text-rose-300" },
  { id: "vacuum_start", label: "扫地机器人", icon: Sparkles, color: "text-emerald-300" },
];

async function execute(actionId: string) {
  loading.value = actionId;
  try {
    const result = await api.executeAction(actionId);
    emit("executed", result.message);
  } finally {
    loading.value = null;
  }
}
</script>
