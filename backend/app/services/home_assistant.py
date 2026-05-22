from typing import Any

import httpx

from app.models.schemas import Device, DeviceCategory, DeviceCategoryId, DeviceStatus


CATEGORY_LABELS: dict[str, str] = {
    "all": "全部设备",
    "light": "灯光",
    "sensor": "传感器",
    "climate": "空调",
    "plug": "插座",
    "lock": "门锁",
    "curtain": "窗帘",
    "vacuum": "扫地机器人",
    "security": "安防设备",
    "unknown": "其他设备",
}

CATEGORY_ORDER = ["all", "light", "sensor", "climate", "plug", "lock", "curtain", "vacuum", "security", "unknown"]


class HomeAssistantClient:
    """Thin Home Assistant REST API wrapper for read-only entity access."""

    def __init__(self, base_url: str, token: str, timeout: float = 8.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def get_states(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/states", headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_state(self, entity_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/states/{entity_id}", headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def call_service(self, domain: str, service: str, service_data: dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/services/{domain}/{service}",
                headers=self.headers,
                json=service_data,
            )
            response.raise_for_status()
            return response.json()


def get_entity_domain(entity_id: str) -> str:
    return entity_id.split(".", 1)[0] if "." in entity_id else "unknown"


def get_device_category(entity_id: str, attributes: dict[str, Any]) -> DeviceCategoryId:
    domain = get_entity_domain(entity_id)
    device_class = str(attributes.get("device_class") or "").lower()

    if domain == "light":
        return "light"
    if domain in {"sensor", "binary_sensor"}:
        if device_class in {"door", "garage_door", "lock", "motion", "occupancy", "opening", "presence", "safety", "smoke"}:
            return "security"
        return "sensor"
    if domain == "climate":
        return "climate"
    if domain in {"switch", "button", "input_button"}:
        if device_class in {"outlet", "plug"} or any(token in entity_id.lower() for token in ("plug", "socket", "outlet")):
            return "plug"
        return "unknown"
    if domain in {"number"} and any(token in entity_id.lower() for token in ("plug", "socket", "outlet", "power")):
        return "plug"
    if domain == "lock":
        return "lock"
    if domain == "cover":
        if device_class in {"curtain", "blind", "shade", "shutter", "awning"}:
            return "curtain"
        return "unknown"
    if domain == "vacuum":
        return "vacuum"
    if domain in {"alarm_control_panel", "camera"}:
        return "security"
    return "unknown"


def get_device_status(raw_state: str) -> DeviceStatus:
    normalized = raw_state.lower()
    if normalized == "unavailable":
        return "offline"
    if normalized == "unknown":
        return "unknown"
    if normalized in {"problem", "detected", "triggered", "jammed"}:
        return "warning"
    return "online"


def state_to_device(state: dict[str, Any]) -> Device:
    attributes = state.get("attributes") or {}
    entity_id = state.get("entity_id", "unknown.unknown")
    domain = get_entity_domain(entity_id)
    friendly_name = attributes.get("friendly_name") or entity_id
    raw_state = str(state.get("state", "unknown"))

    return Device(
        id=entity_id,
        name=friendly_name,
        category=get_device_category(entity_id, attributes),
        room=attributes.get("area_id") or attributes.get("room") or "Home Assistant",
        status=get_device_status(raw_state),
        state=raw_state,
        domain=domain,
        updated_at=state.get("last_updated") or state.get("last_changed"),
        source="home_assistant",
    )


def states_to_devices(states: list[dict[str, Any]]) -> list[Device]:
    return [state_to_device(state) for state in states]


def build_device_categories(devices: list[Device]) -> list[DeviceCategory]:
    counts: dict[str, int] = {category: 0 for category in CATEGORY_ORDER}
    counts["all"] = len(devices)
    for device in devices:
        counts[device.category] = counts.get(device.category, 0) + 1

    return [
        DeviceCategory(id=category, label=CATEGORY_LABELS[category], count=counts.get(category, 0))
        for category in CATEGORY_ORDER
        if category == "all" or counts.get(category, 0) > 0
    ]
