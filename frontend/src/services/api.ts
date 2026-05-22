import type {
  AutomationRule,
  Device,
  DeviceCategory,
  EventItem,
  Metrics,
  Overview,
  Topology,
} from "../types/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; mode: string }>("/api/health"),
  overview: () => request<Overview>("/api/overview"),
  devices: () => request<{ categories: DeviceCategory[]; devices: Device[] }>("/api/devices"),
  topology: () => request<Topology>("/api/topology"),
  metrics: () => request<Metrics>("/api/metrics"),
  events: () => request<EventItem[]>("/api/events/recent"),
  automations: () => request<AutomationRule[]>("/api/automations"),
  executeAction: (actionId: string) =>
    request<{ success: boolean; action_id: string; message: string }>("/api/actions/execute", {
      method: "POST",
      body: JSON.stringify({ action_id: actionId }),
    }),
};
