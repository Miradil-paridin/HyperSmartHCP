<template>
  <main class="h-screen p-5">
    <div class="mx-auto grid h-full max-w-[1920px] grid-rows-[72px_110px_1fr] gap-4">
      <TopNav :api-mode="apiMode" :connected="connected" />

      <OverviewCards v-if="overview" :overview="overview" />

      <section class="grid min-h-0 grid-cols-[300px_1fr_380px] gap-4">
        <Sidebar :categories="categories" :devices="devices" />

        <div class="grid min-h-0 grid-rows-[1fr_300px] gap-4">
          <TopologyGraph v-if="topology" :topology="topology" :device-update="lastDeviceUpdate" />
          <MetricCharts v-if="metrics" :metrics="metrics" />
        </div>

        <aside class="grid min-h-0 grid-rows-[220px_1fr_250px] gap-4">
          <QuickActions :readonly="apiMode === 'home_assistant'" @executed="handleActionExecuted" />
          <EventLog :events="events" />
          <AutomationPanel :rules="automations" />
        </aside>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import AutomationPanel from "./AutomationPanel.vue";
import EventLog from "./EventLog.vue";
import MetricCharts from "./MetricCharts.vue";
import OverviewCards from "./OverviewCards.vue";
import QuickActions from "./QuickActions.vue";
import Sidebar from "./Sidebar.vue";
import TopNav from "./TopNav.vue";
import TopologyGraph from "./TopologyGraph.vue";
import { api } from "../services/api";
import type {
  AutomationRule,
  Device,
  DeviceCategory,
  EventItem,
  Metrics,
  Overview,
  RealtimePayload,
  Topology,
} from "../types/api";

const apiMode = ref("mock");
const connected = ref(false);
const overview = ref<Overview | null>(null);
const categories = ref<DeviceCategory[]>([]);
const devices = ref<Device[]>([]);
const topology = ref<Topology | null>(null);
const metrics = ref<Metrics | null>(null);
const events = ref<EventItem[]>([]);
const automations = ref<AutomationRule[]>([]);
const lastDeviceUpdate = ref<{ id: string; status: Device["status"] } | null>(null);
let socket: WebSocket | null = null;
let reconnectTimer: number | undefined;
let shouldReconnect = true;

async function loadInitialData() {
  const [health, overviewData, deviceData, topologyData, metricsData, eventData, automationData] =
    await Promise.all([
      api.health(),
      api.overview(),
      api.devices(),
      api.topology(),
      api.metrics(),
      api.events(),
      api.automations(),
    ]);

  apiMode.value = health.mode;
  connected.value = health.status === "ok";
  overview.value = overviewData;
  categories.value = deviceData.categories;
  devices.value = deviceData.devices;
  topology.value = topologyData;
  metrics.value = metricsData;
  events.value = eventData;
  automations.value = automationData;
}

function handleActionExecuted(message: string) {
  const event: EventItem = {
    id: `local-${Date.now()}`,
    type: "AUTO",
    message,
    timestamp: new Date().toISOString(),
  };
  events.value = [event, ...events.value].slice(0, 12);
}

function realtimeUrl() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/ws/realtime`;
}

function applyRealtimePayload(payload: RealtimePayload) {
  overview.value = payload.overview;
  metrics.value = payload.metrics;
  events.value = payload.events;
  lastDeviceUpdate.value = { id: payload.device_update.id, status: payload.device_update.status };
  devices.value = devices.value.map((device) =>
    device.id === payload.device_update.id
      ? { ...device, status: payload.device_update.status, state: payload.device_update.state }
      : device,
  );
}

function connectRealtime() {
  socket?.close();
  socket = new WebSocket(realtimeUrl());

  socket.onopen = () => {
    connected.value = true;
  };

  socket.onmessage = (event) => {
    applyRealtimePayload(JSON.parse(event.data) as RealtimePayload);
  };

  socket.onclose = () => {
    connected.value = false;
    if (shouldReconnect) {
      reconnectTimer = window.setTimeout(connectRealtime, 2500);
    }
  };
}

onMounted(() => {
  void loadInitialData().then(() => {
    if (apiMode.value === "mock") {
      connectRealtime();
    }
  });
});

onBeforeUnmount(() => {
  shouldReconnect = false;
  if (reconnectTimer) window.clearTimeout(reconnectTimer);
  socket?.close();
});
</script>
