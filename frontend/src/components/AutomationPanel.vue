<template>
  <section class="glass-panel flex min-h-0 items-center gap-3 rounded-xl p-3">
    <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/7 bg-slate-950/28">
      <Workflow class="h-4.5 w-4.5 text-sky-300" />
    </div>
    <div class="min-w-0 flex-1">
      <div class="flex items-center justify-between gap-3">
        <div>
          <div class="section-kicker">自动化</div>
          <h2 class="text-sm font-bold text-white">规则状态</h2>
        </div>
        <div class="text-right">
          <div class="text-xl font-black text-emerald-200">{{ enabledCount }}</div>
          <div class="text-[10px] text-slate-500">启用</div>
        </div>
      </div>
      <div class="mt-0.5 truncate text-xs text-slate-500">{{ rules[0]?.name ?? "暂无规则" }} · {{ pausedCount }} 条暂停</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Workflow } from "@lucide/vue";
import type { AutomationRule } from "../types/api";

const props = defineProps<{ rules: AutomationRule[] }>();

const enabledCount = computed(() => props.rules.filter((rule) => rule.enabled).length);
const pausedCount = computed(() => props.rules.length - enabledCount.value);
</script>
