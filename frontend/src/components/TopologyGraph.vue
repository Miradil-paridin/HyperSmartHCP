<template>
  <section class="glass-panel tech-border relative min-h-0 rounded-lg p-4">
    <div class="absolute left-4 top-4 z-10 flex items-center gap-3">
      <h2 class="section-title">空间拓扑</h2>
      <span v-if="deviceUpdate" class="rounded border border-cyan/20 bg-cyan/10 px-2 py-1 text-xs text-cyan">
        {{ deviceUpdate.id }} · {{ deviceUpdate.status }}
      </span>
    </div>
    <div ref="graphEl" class="h-full w-full" />
  </section>
</template>

<script setup lang="ts">
import cytoscape, { type Core, type ElementDefinition } from "cytoscape";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import type { Device, Topology } from "../types/api";

const props = defineProps<{
  topology: Topology;
  deviceUpdate?: { id: string; status: Device["status"] } | null;
}>();

const graphEl = ref<HTMLDivElement | null>(null);
let cy: Core | null = null;

const statusColor: Record<string, string> = {
  online: "#5eead4",
  offline: "#fb7185",
  warning: "#fcd34d",
  unknown: "#94a3b8",
};

function elements(): ElementDefinition[] {
  return [
    ...props.topology.nodes.map((node) => ({
      data: { id: node.id, label: node.label, type: node.type, status: node.status },
    })),
    ...props.topology.edges.map((edge) => ({
      data: { id: `${edge.source}-${edge.target}`, source: edge.source, target: edge.target },
    })),
  ];
}

function renderGraph() {
  if (!graphEl.value) return;

  cy?.destroy();
  cy = cytoscape({
    container: graphEl.value,
    elements: elements(),
    wheelSensitivity: 0.25,
    style: [
      {
        selector: "node",
        style: {
          label: "data(label)",
          color: "#dffcff",
          "font-size": 10,
          "text-outline-color": "#020617",
          "text-outline-width": 3,
          "background-color": (node) => statusColor[String(node.data("status"))] ?? "#94a3b8",
          "border-color": "rgba(255,255,255,0.55)",
          "border-width": 1,
          width: 36,
          height: 36,
        },
      },
      {
        selector: 'node[type = "hub"]',
        style: {
          width: 86,
          height: 86,
          "font-size": 13,
          "font-weight": 700,
          "background-color": "#38bdf8",
        },
      },
      {
        selector: 'node[type = "room"]',
        style: {
          width: 58,
          height: 58,
          "background-color": "#a78bfa",
        },
      },
      {
        selector: "edge",
        style: {
          width: 1.2,
          "line-color": "rgba(125,211,252,0.38)",
          "target-arrow-shape": "none",
          "curve-style": "bezier",
        },
      },
    ],
    layout: {
      name: "cose",
      animate: true,
      animationDuration: 900,
      fit: true,
      padding: 72,
      nodeRepulsion: 9000,
      idealEdgeLength: 120,
    },
  });
}

onMounted(renderGraph);

watch(() => props.topology, renderGraph, { deep: true });

watch(
  () => props.deviceUpdate,
  (update) => {
    if (!cy || !update) return;
    cy.getElementById(update.id).animate({ style: { "border-width": 5 } }, { duration: 220 }).animate(
      { style: { "border-width": 1 } },
      { duration: 520 },
    );
  },
);

onBeforeUnmount(() => {
  cy?.destroy();
});
</script>
