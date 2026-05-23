from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from app.models.schemas import Device


ALLOWED_CONTROL_DOMAINS = {"light", "switch", "fan", "climate", "cover"}
BLOCKED_CONTROL_DOMAINS = {"lock", "camera", "alarm_control_panel", "siren"}


@dataclass(frozen=True)
class ServiceCall:
    domain: str
    service: str
    service_data: dict[str, Any]
    action_id: str | None = None
    entity_id: str | None = None
    label: str = "设备控制"


SAFE_ACTIONS: dict[str, ServiceCall] = {
    "all_lights_on": ServiceCall(
        domain="light",
        service="turn_on",
        service_data={"entity_id": "all"},
        action_id="all_lights_on",
        entity_id="all",
        label="打开全屋灯光",
    ),
    "all_lights_off": ServiceCall(
        domain="light",
        service="turn_off",
        service_data={"entity_id": "all"},
        action_id="all_lights_off",
        entity_id="all",
        label="关闭全屋灯光",
    ),
    "all_fans_off": ServiceCall(
        domain="fan",
        service="turn_off",
        service_data={"entity_id": "all"},
        action_id="all_fans_off",
        entity_id="all",
        label="关闭全部风扇",
    ),
    "climate_off": ServiceCall(
        domain="climate",
        service="turn_off",
        service_data={"entity_id": "all"},
        action_id="climate_off",
        entity_id="all",
        label="关闭全部空调",
    ),
    "curtains_open": ServiceCall(
        domain="cover",
        service="open_cover",
        service_data={"entity_id": "all"},
        action_id="curtains_open",
        entity_id="all",
        label="打开全部窗帘",
    ),
    "curtains_close": ServiceCall(
        domain="cover",
        service="close_cover",
        service_data={"entity_id": "all"},
        action_id="curtains_close",
        entity_id="all",
        label="关闭全部窗帘",
    ),
}


def get_entity_domain(entity_id: str) -> str:
    return entity_id.split(".", 1)[0] if "." in entity_id else entity_id


def resolve_service_call(
    *,
    action_id: str | None,
    entity_id: str | None,
    service: str | None,
    service_data: dict[str, Any] | None,
    payload: dict[str, Any] | None,
) -> ServiceCall:
    if action_id:
        if action_id not in SAFE_ACTIONS:
            raise ValueError(f"未知或未开放的快捷动作：{action_id}")
        return SAFE_ACTIONS[action_id]

    if not entity_id or not service:
        raise ValueError("必须提供 action_id 或 entity_id + service")

    data = dict(payload or {})
    data.update(service_data or {})
    data["entity_id"] = entity_id

    return ServiceCall(
        domain=get_entity_domain(entity_id),
        service=service,
        service_data=data,
        entity_id=entity_id,
        label=f"{entity_id}.{service}",
    )


def validate_service_call(call: ServiceCall) -> None:
    if call.domain in BLOCKED_CONTROL_DOMAINS:
        raise PermissionError(f"{call.domain} 设备类型暂未开放控制")
    if call.domain not in ALLOWED_CONTROL_DOMAINS:
        raise PermissionError(f"{call.domain} 设备类型暂未开放控制")


def expand_action_calls(action_id: str, devices: Iterable[Device]) -> list[ServiceCall]:
    if action_id not in SAFE_ACTIONS:
        raise ValueError(f"未知或未开放的快捷动作：{action_id}")

    online_devices = [
        device for device in devices if device.controllable and device.status != "offline" and device.state != "unavailable"
    ]

    if action_id == "all_lights_on":
        return build_grouped_calls(
            select_devices(online_devices, category="light", domains={"light", "switch"}),
            service="turn_on",
            action_id=action_id,
            label="打开全屋灯光",
        )
    if action_id == "all_lights_off":
        return build_grouped_calls(
            select_devices(online_devices, category="light", domains={"light", "switch"}),
            service="turn_off",
            action_id=action_id,
            label="关闭全屋灯光",
        )
    if action_id == "all_fans_off":
        return build_grouped_calls(
            select_devices(online_devices, domains={"fan"}),
            service="turn_off",
            action_id=action_id,
            label="关闭全部风扇",
        )
    if action_id == "climate_off":
        return build_grouped_calls(
            select_devices(online_devices, domains={"climate"}),
            service="turn_off",
            action_id=action_id,
            label="关闭全部空调",
        )
    if action_id == "curtains_open":
        return build_grouped_calls(
            select_devices(online_devices, category="curtain", domains={"cover"}),
            service="open_cover",
            action_id=action_id,
            label="打开全部窗帘",
        )
    if action_id == "curtains_close":
        return build_grouped_calls(
            select_devices(online_devices, category="curtain", domains={"cover"}),
            service="close_cover",
            action_id=action_id,
            label="关闭全部窗帘",
        )

    return [SAFE_ACTIONS[action_id]]


def select_devices(devices: Iterable[Device], *, category: str | None = None, domains: set[str] | None = None) -> list[Device]:
    selected = []
    for device in devices:
        if category is not None and device.category != category:
            continue
        if domains is not None and device.domain not in domains:
            continue
        selected.append(device)
    return selected


def build_grouped_calls(devices: Iterable[Device], *, service: str, action_id: str, label: str) -> list[ServiceCall]:
    grouped: dict[str, list[str]] = {}
    for device in devices:
        grouped.setdefault(device.domain, []).append(device.id)

    calls = [
        ServiceCall(
            domain=domain,
            service=service,
            service_data={"entity_id": entity_ids},
            action_id=action_id,
            entity_id=",".join(entity_ids),
            label=label,
        )
        for domain, entity_ids in grouped.items()
    ]

    if calls:
        return calls

    fallback = SAFE_ACTIONS[action_id]
    return [fallback]
