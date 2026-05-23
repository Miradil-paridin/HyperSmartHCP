<template>
  <BigScreen
    v-if="activePage === 'screen'"
    :api-mode="apiMode"
    :connected="connected"
    :overview="overview"
    :metrics="metrics"
    :events="events"
    :automations="automations"
    :room-summaries="roomSummaries"
    :type-summaries="typeSummaries"
    @update:active-page="activePage = $event"
  />

  <main v-else class="console-page">
    <div class="grid min-h-0 min-w-0 grid-rows-[74px_120px_minmax(0,1fr)_220px] gap-4">
      <TopNav :api-mode="apiMode" :connected="connected" :active-page="activePage" @update:active-page="activePage = $event" />

      <OverviewCards v-if="overview" :overview="overview" />

      <section class="grid min-h-0 min-w-0 grid-cols-[320px_minmax(0,1fr)_380px] gap-4 overflow-hidden">
        <Sidebar
          :categories="displayCategories"
          :rooms="rooms"
          :devices="filteredDevices"
          :selected-category="selectedCategory"
          :selected-room="selectedRoom"
          :selected-status="selectedStatus"
          :filtered-count="filteredDevices.length"
          @update:selected-category="selectedCategory = $event"
          @update:selected-room="selectedRoom = $event"
          @update:selected-status="selectedStatus = $event"
        />

        <HomeMap
          :mode="topologyMode"
          :room-summaries="roomSummaries"
          :type-summaries="typeSummaries"
          :selected-id="selectedNode?.id ?? null"
          @update:mode="topologyMode = $event"
          @select="selectNode"
        />

        <aside class="grid min-h-0 min-w-0 grid-rows-[minmax(0,225px)_minmax(0,1fr)_88px] gap-4 overflow-hidden">
          <QuickActions :selected-context="selectedContext" @executed="handleActionExecuted" />
          <EventLog :events="events" />
          <AutomationPanel :rules="automations" />
        </aside>
      </section>

      <MetricCharts v-if="metrics" class="min-h-0 min-w-0 overflow-hidden" :metrics="metrics" />
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import AutomationPanel from "./AutomationPanel.vue";
import BigScreen from "./BigScreen.vue";
import EventLog from "./EventLog.vue";
import HomeMap from "./HomeMap.vue";
import MetricCharts from "./MetricCharts.vue";
import OverviewCards from "./OverviewCards.vue";
import QuickActions, { type SelectedContext } from "./QuickActions.vue";
import Sidebar from "./Sidebar.vue";
import TopNav from "./TopNav.vue";
import { useHomeInsights, type StatusFilter, type TopologyMode } from "../composables/useHomeInsights";
import { api } from "../services/api";
import type { AutomationRule, Device, DeviceCategory, EventItem, Metrics, Overview, RealtimePayload, Topology } from "../types/api";

const activePage = ref<"console" | "screen">("console");
const apiMode = ref("mock");
const connected = ref(false);
const overview = ref<Overview | null>(null);
const categories = ref<DeviceCategory[]>([]);
const devices = ref<Device[]>([]);
const topology = ref<Topology | null>(null);
const metrics = ref<Metrics | null>(null);
const events = ref<EventItem[]>([]);
const automations = ref<AutomationRule[]>([]);

const selectedCategory = ref("all");
const selectedRoom = ref("all");
const selectedStatus = ref<StatusFilter>("all");
const topologyMode = ref<TopologyMode>("type");
const selectedNode = ref<{ type: TopologyMode; id: string } | null>(null);

const { rooms, displayCategories, filteredDevices, roomSummaries, typeSummaries, preferredTopologyMode } = useHomeInsights(
  devices,
  categories,
  metrics,
  selectedCategory,
  selectedRoom,
  selectedStatus,
);

const systemContext = computed<SelectedContext>(() => ({
  name: "系统摘要",
  subtitle: "默认显示全屋实体状态，点击中间节点查看分组详情。",
  deviceCount: filteredDevices.value.length,
  onlineCount: filteredDevices.value.filter((device) => device.status === "online").length,
  abnormalCount: filteredDevices.value.filter((device) => ["offline", "warning", "unknown"].includes(device.status)).length,
  devices: filteredDevices.value.slice(0, 8),
}));

const selectedContext = computed<SelectedContext>(() => {
  if (!selectedNode.value) return systemContext.value;
  if (selectedNode.value.type === "room") {
    const room = roomSummaries.value.find((item) => item.id === selectedNode.value?.id);
    if (!room) return systemContext.value;
    return {
      name: room.name,
      subtitle: `${room.temperature ?? "--"} / ${room.humidity ?? "--"} · 房间总览`,
      deviceCount: room.deviceCount,
      onlineCount: room.onlineCount,
      abnormalCount: room.abnormalCount,
      devices: room.devices,
    };
  }

  const group = typeSummaries.value.find((item) => item.id === selectedNode.value?.id);
  if (!group) return systemContext.value;
  return {
    name: group.name,
    subtitle: "设备类型总览",
    deviceCount: group.deviceCount,
    onlineCount: group.onlineCount,
    abnormalCount: group.abnormalCount,
    devices: group.devices,
  };
});

let socket: WebSocket | null = null;
let reconnectTimer: number | undefined;
let shouldReconnect = true;

async function loadInitialData() {
  const [health, overviewData, deviceData, topologyData, metricsData, eventData, automationData] = await Promise.all([
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
  topologyMode.value = preferredTopologyMode.value;
}

async function refreshHomeAssistantData() {
  const [overviewData, deviceData, topologyData, eventData] = await Promise.all([
    api.overview(),
    api.devices(),
    api.topology(),
    api.events(),
  ]);
  overview.value = overviewData;
  categories.value = deviceData.categories;
  devices.value = deviceData.devices;
  topology.value = topologyData;
  events.value = eventData;
}

async function handleActionExecuted(message: string) {
  const event: EventItem = {
    id: `local-${Date.now()}`,
    type: "AUTO",
    message,
    timestamp: new Date().toISOString(),
  };
  events.value = [event, ...events.value].slice(0, 12);

  if (apiMode.value === "home_assistant") {
    await refreshHomeAssistantData();
  }
}

function selectNode(selection: { type: TopologyMode; id: string }) {
  selectedNode.value = selection;
}

function realtimeUrl() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/ws/realtime`;
}

function applyRealtimePayload(payload: RealtimePayload) {
  overview.value = payload.overview;
  metrics.value = payload.metrics;
  events.value = payload.events;
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

watch(preferredTopologyMode, (mode) => {
  if (!selectedNode.value) topologyMode.value = mode;
});

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
