import { computed, type Ref } from "vue";
import type { Device, DeviceCategory, Metrics } from "../types/api";

export type StatusFilter = "all" | "online" | "abnormal" | "offline";
export type TopologyMode = "room" | "type";

export type DeviceGroup = {
  id: string;
  name: string;
  kind: TopologyMode;
  deviceCount: number;
  onlineCount: number;
  abnormalCount: number;
  offlineCount: number;
  warningCount: number;
  temperature?: string;
  humidity?: string;
  devices: Device[];
};

export type RoomSummary = DeviceGroup;
export type TypeSummary = DeviceGroup;

const fallbackRooms = ["全屋"];

const categoryLabels: Record<string, string> = {
  all: "全部设备",
  light: "灯光",
  sensor: "传感器",
  climate: "空调",
  plug: "插座 / 开关",
  lock: "门锁",
  curtain: "窗帘",
  vacuum: "扫地机器人",
  security: "安防",
  media: "媒体设备",
  unknown: "其他",
};

const categoryOrder = ["light", "sensor", "plug", "curtain", "climate", "security", "vacuum", "lock", "media", "unknown"];

export function useHomeInsights(
  devices: Ref<Device[]>,
  categories: Ref<DeviceCategory[]>,
  metrics: Ref<Metrics | null>,
  selectedCategory: Ref<string>,
  selectedRoom: Ref<string>,
  selectedStatus: Ref<StatusFilter>,
) {
  const normalizedDevices = computed(() => devices.value.map((device) => ({ ...device, room: normalizeRoom(device.room) })));

  const rooms = computed(() => {
    const unique = Array.from(new Set(normalizedDevices.value.map((device) => device.room).filter(Boolean)));
    return unique.length ? unique : fallbackRooms;
  });

  const displayCategories = computed<DeviceCategory[]>(() => {
    const counts = new Map<string, number>();
    for (const device of normalizedDevices.value) {
      const category = normalizeCategory(device.category, device.domain);
      counts.set(category, (counts.get(category) ?? 0) + 1);
    }

    const known = categoryOrder
      .filter((id) => counts.has(id))
      .map((id) => ({ id, label: categoryLabels[id] ?? id, count: counts.get(id) ?? 0 }));

    return [{ id: "all", label: "全部设备", count: normalizedDevices.value.length }, ...known];
  });

  const filteredDevices = computed(() =>
    normalizedDevices.value.filter((device) => {
      const normalizedCategory = normalizeCategory(device.category, device.domain);
      const categoryMatches = selectedCategory.value === "all" || normalizedCategory === selectedCategory.value;
      const roomMatches = selectedRoom.value === "all" || device.room === selectedRoom.value;
      const statusMatches =
        selectedStatus.value === "all" ||
        device.status === selectedStatus.value ||
        (selectedStatus.value === "abnormal" && isAbnormal(device));
      return categoryMatches && roomMatches && statusMatches;
    }),
  );

  const roomSummaries = computed<RoomSummary[]>(() => {
    const groups = new Map<string, Device[]>();
    for (const room of rooms.value) groups.set(room, []);
    for (const device of filteredDevices.value) {
      const room = device.room || "未分区";
      groups.set(room, [...(groups.get(room) ?? []), device]);
    }

    return Array.from(groups.entries())
      .map(([room, roomDevices], index) => createGroup(`room-${index}-${room}`, room, "room", roomDevices, metrics.value))
      .filter((room) => room.deviceCount > 0);
  });

  const typeSummaries = computed<TypeSummary[]>(() =>
    displayCategories.value
      .filter((category) => category.id !== "all")
      .map((category) => {
        const typeDevices = filteredDevices.value.filter(
          (device) => normalizeCategory(device.category, device.domain) === category.id,
        );
        return createGroup(category.id, category.label, "type", typeDevices, metrics.value);
      })
      .filter((group) => group.deviceCount > 0),
  );

  const preferredTopologyMode = computed<TopologyMode>(() => {
    const usefulRooms = roomSummaries.value.filter((room) => !["Home Assistant", "未分区", "全屋"].includes(room.name));
    return usefulRooms.length >= 2 ? "room" : "type";
  });

  return { rooms, displayCategories, filteredDevices, roomSummaries, typeSummaries, preferredTopologyMode };
}

export function normalizeCategory(category: string, domain?: string) {
  if (category !== "unknown") return category;
  if (domain === "media_player") return "media";
  if (domain === "switch") return "plug";
  if (domain === "fan") return "climate";
  if (domain === "binary_sensor") return "sensor";
  return "unknown";
}

export function isAbnormal(device: Device) {
  return ["offline", "warning", "unknown"].includes(device.status) || ["unavailable", "unknown"].includes(device.state);
}

export function shortEntity(value: string, head = 18, tail = 10) {
  return value.length > head + tail + 3 ? `${value.slice(0, head)}...${value.slice(-tail)}` : value;
}

export function readableEvent(message: string) {
  return message
    .replace(/([a-z_]+\.)[a-zA-Z0-9_]+\b/g, (match) => shortEntity(match, 12, 8))
    .replace(/turn_on/g, "开启")
    .replace(/turn_off/g, "关闭")
    .replace(/unavailable/g, "不可用");
}

function normalizeRoom(room: string) {
  if (!room || room === "unknown") return "未分区";
  return room;
}

function createGroup(id: string, name: string, kind: TopologyMode, groupDevices: Device[], metrics: Metrics | null): DeviceGroup {
  const offlineCount = groupDevices.filter((device) => device.status === "offline").length;
  const warningCount = groupDevices.filter((device) => ["warning", "unknown"].includes(device.status)).length;
  return {
    id,
    name,
    kind,
    deviceCount: groupDevices.length,
    onlineCount: groupDevices.filter((device) => device.status === "online").length,
    abnormalCount: groupDevices.filter(isAbnormal).length,
    offlineCount,
    warningCount,
    temperature: groupMetric(groupDevices, "temperature", metrics),
    humidity: groupMetric(groupDevices, "humidity", metrics),
    devices: groupDevices,
  };
}

function groupMetric(devices: Device[], kind: "temperature" | "humidity", metrics: Metrics | null) {
  const keyword = kind === "temperature" ? /温|temp|temperature/i : /湿|humidity/i;
  const sensor = devices.find((device) => device.category === "sensor" && keyword.test(`${device.name} ${device.id}`));
  if (sensor && !["unknown", "unavailable"].includes(sensor.state)) return sensor.state;

  const series = metrics?.series[kind];
  const value = series?.length ? series[series.length - 1] : null;
  if (value === null || value === undefined) return undefined;
  return kind === "temperature" ? `${value} C` : `${value} %`;
}
