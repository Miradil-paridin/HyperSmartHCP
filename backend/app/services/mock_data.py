from __future__ import annotations

import math
import random
from datetime import datetime, timedelta, timezone
from typing import Any

from app.services.event_log import get_action_events


DEVICE_CATEGORIES = [
    {"id": "all", "label": "全部设备", "count": 18},
    {"id": "light", "label": "灯光", "count": 6},
    {"id": "sensor", "label": "传感器", "count": 4},
    {"id": "climate", "label": "空调", "count": 2},
    {"id": "plug", "label": "插座", "count": 2},
    {"id": "lock", "label": "门锁", "count": 1},
    {"id": "curtain", "label": "窗帘", "count": 1},
    {"id": "vacuum", "label": "扫地机器人", "count": 1},
    {"id": "security", "label": "安防设备", "count": 1},
]

DEVICES = [
    {"id": "light.living_main", "name": "客厅主灯", "category": "light", "room": "客厅", "status": "online", "state": "on"},
    {"id": "light.living_ambient", "name": "客厅氛围灯", "category": "light", "room": "客厅", "status": "online", "state": "on"},
    {"id": "sensor.living_motion", "name": "客厅人体传感器", "category": "sensor", "room": "客厅", "status": "online", "state": "clear"},
    {"id": "sensor.living_temp", "name": "温湿度传感器", "category": "sensor", "room": "客厅", "status": "online", "state": "25.2 C"},
    {"id": "climate.living_ac", "name": "客厅空调", "category": "climate", "room": "客厅", "status": "online", "state": "cool"},
    {"id": "plug.tv_wall", "name": "电视墙插座", "category": "plug", "room": "客厅", "status": "online", "state": "76 W"},
    {"id": "curtain.balcony", "name": "阳台窗帘", "category": "curtain", "room": "阳台", "status": "online", "state": "open"},
    {"id": "vacuum.robot", "name": "扫地机器人", "category": "vacuum", "room": "客厅", "status": "online", "state": "docked"},
    {"id": "lock.front_door", "name": "入户门锁", "category": "lock", "room": "玄关", "status": "online", "state": "locked"},
    {"id": "sensor.door_contact", "name": "门窗传感器", "category": "security", "room": "玄关", "status": "online", "state": "closed"},
    {"id": "light.bedroom_main", "name": "卧室主灯", "category": "light", "room": "卧室", "status": "offline", "state": "unavailable"},
    {"id": "light.bedside", "name": "床头灯", "category": "light", "room": "卧室", "status": "online", "state": "off"},
    {"id": "climate.bedroom_ac", "name": "卧室空调", "category": "climate", "room": "卧室", "status": "online", "state": "standby"},
    {"id": "sensor.bedroom_temp", "name": "卧室温湿度", "category": "sensor", "room": "卧室", "status": "online", "state": "24.7 C"},
    {"id": "light.kitchen", "name": "厨房灯", "category": "light", "room": "厨房", "status": "online", "state": "off"},
    {"id": "plug.kettle", "name": "热水壶插座", "category": "plug", "room": "厨房", "status": "warning", "state": "980 W"},
    {"id": "light.bathroom", "name": "卫生间灯", "category": "light", "room": "卫生间", "status": "online", "state": "off"},
    {"id": "sensor.bathroom_humidity", "name": "卫生间湿度", "category": "sensor", "room": "卫生间", "status": "unknown", "state": "unknown"},
]

AUTOMATIONS = [
    {"id": "auto_hot_ac", "name": "温度过高开空调", "enabled": True, "trigger": "客厅温度 > 28 C", "action": "开启客厅空调"},
    {"id": "auto_motion_light", "name": "有人经过开灯", "enabled": True, "trigger": "人体传感器检测到移动", "action": "开启对应房间灯光"},
    {"id": "auto_away_lights", "name": "离家关闭全屋灯", "enabled": True, "trigger": "离家模式启用", "action": "关闭全部灯光"},
    {"id": "auto_night_light", "name": "夜间小夜灯", "enabled": False, "trigger": "23:30-06:30 有人经过", "action": "开启低亮度灯光"},
]

ACTION_MESSAGES = {
    "all_lights_on": "已模拟打开全部灯光",
    "all_lights_off": "已模拟关闭全部灯光",
    "all_fans_off": "已模拟关闭全部风扇",
    "climate_off": "已模拟关闭全部空调",
    "curtains_open": "已模拟打开全部窗帘",
    "curtains_close": "已模拟关闭全部窗帘",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_overview() -> dict[str, Any]:
    total = len(DEVICES)
    online = sum(1 for item in DEVICES if item["status"] == "online")
    offline = sum(1 for item in DEVICES if item["status"] == "offline")
    warning = sum(1 for item in DEVICES if item["status"] == "warning")
    health = round(((online / total) * 100) - warning * 3, 1)

    return {
        "total_devices": total,
        "online_devices": online,
        "offline_devices": offline,
        "today_events": 42,
        "home_health": max(0, min(100, health)),
        "updated_at": now_iso(),
    }


def get_devices() -> dict[str, Any]:
    return {"categories": DEVICE_CATEGORIES, "devices": DEVICES}


def get_topology() -> dict[str, Any]:
    rooms = ["客厅", "卧室", "厨房", "卫生间", "阳台", "玄关"]
    nodes = [{"id": "home", "label": "HyperLink Home", "type": "hub", "status": "online"}]
    edges = []

    for room in rooms:
        room_id = f"room.{room}"
        nodes.append({"id": room_id, "label": room, "type": "room", "status": "online"})
        edges.append({"source": "home", "target": room_id})

    for device in DEVICES:
        nodes.append(
            {
                "id": device["id"],
                "label": device["name"],
                "type": "device",
                "category": device["category"],
                "status": device["status"],
            }
        )
        edges.append({"source": f"room.{device['room']}", "target": device["id"]})

    return {"nodes": nodes, "edges": edges}


def get_metrics(points: int = 24) -> dict[str, Any]:
    start = datetime.now() - timedelta(minutes=(points - 1) * 5)
    labels = [(start + timedelta(minutes=index * 5)).strftime("%H:%M") for index in range(points)]

    def wave(base: float, amplitude: float, noise: float) -> list[float]:
        return [
            round(base + math.sin(index / 3) * amplitude + random.uniform(-noise, noise), 1)
            for index in range(points)
        ]

    return {
        "labels": labels,
        "series": {
            "temperature": wave(25.1, 1.8, 0.3),
            "humidity": wave(53.0, 6.0, 1.6),
            "illuminance": wave(420.0, 160.0, 28.0),
            "power": wave(185.0, 95.0, 18.0),
        },
        "updated_at": now_iso(),
    }


def get_recent_events(limit: int = 12) -> list[dict[str, Any]]:
    action_events = get_action_events()
    templates = [
        ("DEVICE", "客厅主灯状态变更为开启"),
        ("INFO", "Home Assistant mock 数据同步完成"),
        ("WARN", "热水壶插座功率偏高"),
        ("AUTO", "观影模式预案已就绪"),
        ("DEVICE", "阳台窗帘位置更新为打开"),
        ("INFO", "WebSocket 实时通道保持在线"),
        ("ERROR", "卧室主灯暂时离线"),
        ("DEVICE", "扫地机器人回到充电座"),
    ]
    current = datetime.now()
    mock_events = [
        {
            "id": f"event-{index}",
            "type": event_type,
            "message": message,
            "timestamp": (current - timedelta(minutes=index * 7)).isoformat(),
        }
        for index, (event_type, message) in enumerate(templates[:limit])
    ]
    return (action_events + mock_events)[:limit]


def get_automations() -> list[dict[str, Any]]:
    return AUTOMATIONS


def execute_action(action_id: str) -> dict[str, Any]:
    return {
        "success": action_id in ACTION_MESSAGES,
        "action_id": action_id,
        "message": ACTION_MESSAGES.get(action_id, f"未知动作 {action_id}，已按 mock 请求记录"),
    }


def get_realtime_payload() -> dict[str, Any]:
    overview = get_overview()
    metrics = get_metrics(points=12)
    recent_events = get_recent_events(limit=5)
    device = random.choice(DEVICES)
    status = random.choice(["online", "online", "online", "warning", "offline"])

    return {
        "type": "snapshot",
        "timestamp": now_iso(),
        "overview": overview,
        "metrics": metrics,
        "device_update": {
            "id": device["id"],
            "name": device["name"],
            "status": status,
            "state": device["state"],
        },
        "events": recent_events,
    }
