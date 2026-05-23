export interface Overview {
  total_devices: number;
  online_devices: number;
  offline_devices: number;
  today_events: number;
  home_health: number;
  updated_at: string;
}

export interface DeviceCategory {
  id: string;
  label: string;
  count: number;
}

export interface Device {
  id: string;
  name: string;
  category: string;
  room: string;
  status: "online" | "offline" | "warning" | "unknown";
  state: string;
  domain?: string;
  controllable?: boolean;
  updated_at?: string | null;
  source?: "mock" | "home_assistant";
}

export interface TopologyNode {
  id: string;
  label: string;
  type: "hub" | "room" | "device";
  status: "online" | "offline" | "warning" | "unknown";
  category?: string;
}

export interface TopologyEdge {
  source: string;
  target: string;
}

export interface Topology {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
}

export interface Metrics {
  labels: string[];
  series: {
    temperature: number[];
    humidity: number[];
    illuminance: number[];
    power: number[];
  };
  updated_at: string;
}

export interface EventItem {
  id: string;
  type: "INFO" | "WARN" | "ERROR" | "DEVICE" | "AUTO";
  message: string;
  timestamp: string;
}

export interface AutomationRule {
  id: string;
  name: string;
  enabled: boolean;
  trigger: string;
  action: string;
}

export interface RealtimePayload {
  type: "snapshot";
  timestamp: string;
  overview: Overview;
  metrics: Metrics;
  device_update: Pick<Device, "id" | "name" | "status" | "state">;
  events: EventItem[];
}
