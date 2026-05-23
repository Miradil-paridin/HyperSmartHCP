from __future__ import annotations

from typing import Any

import httpx

from app.models.schemas import Device, DeviceCategory, DeviceCategoryId, DeviceStatus
from app.services.action_safety import ALLOWED_CONTROL_DOMAINS


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

LIGHT_KEYWORDS = (
    "light",
    "lamp",
    "bulb",
    "灯",
    "燈",
    "照明",
    "吊灯",
    "吸顶灯",
    "台灯",
    "夜灯",
    "灯带",
    "鞋柜",
    "玄关",
)
INDICATOR_KEYWORDS = ("indicator", "指示灯")
PLUG_KEYWORDS = ("plug", "socket", "outlet", "插座", "插孔", "插线板", "排插")
FAN_KEYWORDS = ("fan", "风扇", "循环扇")
CURTAIN_KEYWORDS = ("curtain", "blind", "shade", "shutter", "窗帘", "窗纱")


class HomeAssistantClient:
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


def normalize_text(*parts: str) -> str:
    return " ".join(part for part in parts if part).lower()


def has_any_keyword(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def is_indicator_entity(entity_id: str, friendly_name: str) -> bool:
    return has_any_keyword(normalize_text(entity_id, friendly_name), INDICATOR_KEYWORDS)


def infer_switch_category(entity_id: str, friendly_name: str, device_class: str) -> DeviceCategoryId:
    normalized = normalize_text(entity_id, friendly_name, device_class)
    if device_class in {"outlet", "plug"} or has_any_keyword(normalized, PLUG_KEYWORDS):
        return "plug"
    if has_any_keyword(normalized, CURTAIN_KEYWORDS):
        return "curtain"
    if has_any_keyword(normalized, FAN_KEYWORDS):
        return "unknown"
    if has_any_keyword(normalized, LIGHT_KEYWORDS) and not is_indicator_entity(entity_id, friendly_name):
        return "light"
    return "unknown"


def get_device_category(entity_id: str, attributes: dict[str, Any]) -> DeviceCategoryId:
    domain = get_entity_domain(entity_id)
    device_class = str(attributes.get("device_class") or "").lower()
    friendly_name = str(attributes.get("friendly_name") or entity_id)

    if domain == "light":
        return "unknown" if is_indicator_entity(entity_id, friendly_name) else "light"
    if domain in {"sensor", "binary_sensor"}:
        if device_class in {"door", "garage_door", "lock", "motion", "occupancy", "opening", "presence", "safety", "smoke"}:
            return "security"
        return "sensor"
    if domain == "climate":
        return "climate"
    if domain == "switch":
        return infer_switch_category(entity_id, friendly_name, device_class)
    if domain in {"button", "input_button"}:
        return "unknown"
    if domain == "number" and has_any_keyword(normalize_text(entity_id, friendly_name), PLUG_KEYWORDS + ("power",)):
        return "plug"
    if domain == "lock":
        return "lock"
    if domain == "cover":
        if device_class in {"curtain", "blind", "shade", "shutter", "awning"} or has_any_keyword(
            normalize_text(entity_id, friendly_name), CURTAIN_KEYWORDS
        ):
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


def is_controllable(domain: str, category: DeviceCategoryId, friendly_name: str, entity_id: str) -> bool:
    if domain == "switch" and category == "light":
        return True
    if domain == "light" and is_indicator_entity(entity_id, friendly_name):
        return False
    return domain in ALLOWED_CONTROL_DOMAINS


def state_to_device(state: dict[str, Any]) -> Device:
    attributes = state.get("attributes") or {}
    entity_id = state.get("entity_id", "unknown.unknown")
    domain = get_entity_domain(entity_id)
    friendly_name = str(attributes.get("friendly_name") or entity_id)
    raw_state = str(state.get("state", "unknown"))
    category = get_device_category(entity_id, attributes)

    return Device(
        id=entity_id,
        name=friendly_name,
        category=category,
        room=attributes.get("area_id") or attributes.get("room") or "Home Assistant",
        status=get_device_status(raw_state),
        state=raw_state,
        domain=domain,
        controllable=is_controllable(domain, category, friendly_name, entity_id),
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


def build_topology_from_devices(devices: list[Device]) -> dict[str, Any]:
    rooms = sorted({device.room for device in devices if device.room})
    nodes: list[dict[str, Any]] = [{"id": "home", "label": "HyperLink Home", "type": "hub", "status": "online"}]
    edges: list[dict[str, str]] = []

    for room in rooms:
        room_id = f"room.{room}"
        room_devices = [device for device in devices if device.room == room]
        if any(device.status == "warning" for device in room_devices):
            room_status: DeviceStatus = "warning"
        elif room_devices and all(device.status == "offline" for device in room_devices):
            room_status = "offline"
        elif any(device.status == "online" for device in room_devices):
            room_status = "online"
        else:
            room_status = "unknown"

        nodes.append({"id": room_id, "label": room, "type": "room", "status": room_status})
        edges.append({"source": "home", "target": room_id})

    for device in devices:
        nodes.append(
            {
                "id": device.id,
                "label": device.name,
                "type": "device",
                "category": device.category,
                "status": device.status,
            }
        )
        edges.append({"source": f"room.{device.room}", "target": device.id})

    return {"nodes": nodes, "edges": edges}
