from __future__ import annotations

from datetime import datetime
from typing import Literal


EventType = Literal["INFO", "WARN", "ERROR", "DEVICE", "AUTO"]

_ACTION_EVENTS: list[dict[str, str]] = []


def record_event(event_type: EventType, message: str) -> dict[str, str]:
    event = {
        "id": f"event-action-{datetime.now().timestamp()}",
        "type": event_type,
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }
    _ACTION_EVENTS.insert(0, event)
    del _ACTION_EVENTS[50:]
    return event


def get_action_events(limit: int | None = None) -> list[dict[str, str]]:
    if limit is None:
        return list(_ACTION_EVENTS)
    return list(_ACTION_EVENTS[:limit])
