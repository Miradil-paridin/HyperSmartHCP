<template>
  <section class="glass-panel tech-border flex min-h-0 flex-col rounded-xl p-3">
    <div class="mb-2 flex items-center justify-between gap-3">
      <div>
        <div class="section-kicker">场景中心</div>
        <h2 class="mt-1 text-base font-bold text-white">快捷场景</h2>
      </div>
      <span class="panel-chip">安全代理</span>
    </div>

    <div class="grid grid-cols-3 gap-2">
      <button
        v-for="scene in scenes"
        :key="scene.id"
        class="scene-button"
        :disabled="loading === scene.id"
        @click="executeScene(scene)"
      >
        <component :is="scene.icon" class="h-4 w-4" :class="scene.color" />
        <span class="truncate">{{ scene.label }}</span>
      </button>
    </div>

    <div class="mt-3 min-h-0 flex-1 rounded-xl border border-sky-300/10 bg-slate-950/26 p-3">
      <div class="mb-2 flex items-center justify-between">
        <div class="text-xs font-bold tracking-[0.14em] text-slate-500">当前选中详情</div>
        <Info class="h-4 w-4 text-slate-500" />
      </div>

      <div>
        <div class="truncate text-base font-black text-white" :title="selectedContext.name">{{ selectedContext.name }}</div>
        <div class="mt-1 truncate text-xs text-slate-500" :title="selectedContext.subtitle">{{ selectedContext.subtitle }}</div>
        <div class="mt-2 grid grid-cols-3 gap-2 rounded-lg bg-black/12 px-3 py-2">
          <div>
            <div class="text-base font-black text-white">{{ selectedContext.deviceCount }}</div>
            <div class="text-[10px] text-slate-500">实体</div>
          </div>
          <div>
            <div class="text-base font-black text-emerald-200">{{ selectedContext.onlineCount }}</div>
            <div class="text-[10px] text-slate-500">在线</div>
          </div>
          <div>
            <div class="text-base font-black text-rose-200">{{ selectedContext.abnormalCount }}</div>
            <div class="text-[10px] text-slate-500">异常</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Armchair, Clapperboard, Home, Info, LightbulbOff, Moon, ShieldCheck } from "@lucide/vue";
import { api } from "../services/api";
import type { Device } from "../types/api";

export type SelectedContext = {
  name: string;
  subtitle: string;
  deviceCount: number;
  onlineCount: number;
  abnormalCount: number;
  devices: Device[];
};

defineProps<{ selectedContext: SelectedContext }>();
const emit = defineEmits<{ executed: [message: string] }>();

const loading = ref<string | null>(null);

const scenes = [
  { id: "home_mode", label: "回家模式", icon: Home, color: "text-sky-300" },
  { id: "away_mode", label: "离家模式", icon: Armchair, color: "text-teal-300" },
  { id: "sleep_mode", label: "睡眠模式", icon: Moon, color: "text-violet-300" },
  { id: "movie_mode", label: "观影模式", icon: Clapperboard, color: "text-amber-300" },
  { id: "all_lights_off", label: "全屋关灯", icon: LightbulbOff, color: "text-rose-300", actionId: "all_lights_off" },
  { id: "security_arm", label: "安防布防", icon: ShieldCheck, color: "text-slate-300" },
];

async function executeScene(scene: (typeof scenes)[number]) {
  if (!scene.actionId) {
    emit("executed", `${scene.label} 已记录为预设场景，真实联动将在后续版本接入。`);
    return;
  }

  loading.value = scene.id;
  try {
    const result = await api.executeAction(scene.actionId);
    emit("executed", result.message);
  } catch (error) {
    emit("executed", error instanceof Error ? error.message : "控制请求失败");
  } finally {
    loading.value = null;
  }
}

</script>
