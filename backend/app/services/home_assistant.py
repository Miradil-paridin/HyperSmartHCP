from typing import Any

import httpx


class HomeAssistantClient:
    """Thin Home Assistant API wrapper reserved for real integrations."""

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

    async def get_events(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/events", headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def call_service(self, domain: str, service: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/services/{domain}/{service}",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()


def state_to_device(state: dict[str, Any]) -> dict[str, Any]:
    attributes = state.get("attributes") or {}
    entity_id = state.get("entity_id", "unknown.unknown")
    domain = entity_id.split(".", 1)[0]
    friendly_name = attributes.get("friendly_name") or entity_id
    raw_state = state.get("state", "unknown")

    return {
        "id": entity_id,
        "name": friendly_name,
        "category": domain,
        "room": attributes.get("area_id") or "Home Assistant",
        "status": "offline" if raw_state in {"unavailable", "unknown"} else "online",
        "state": raw_state,
        "updated_at": state.get("last_updated"),
    }
