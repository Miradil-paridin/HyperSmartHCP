import asyncio
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import get_settings
from app.models.schemas import ActionRequest, ActionResponse
from app.services.home_assistant import HomeAssistantClient, state_to_device
from app.services.mock_data import (
    execute_action,
    get_automations,
    get_devices,
    get_metrics,
    get_overview,
    get_recent_events,
    get_realtime_payload,
    get_topology,
)

router = APIRouter()
ws_router = APIRouter()


@router.get("/health")
async def health() -> dict[str, Any]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "mode": "home_assistant" if settings.use_home_assistant else "mock",
    }


@router.get("/overview")
async def overview() -> dict[str, Any]:
    return get_overview()


@router.get("/devices")
async def devices() -> dict[str, Any]:
    settings = get_settings()
    if settings.use_home_assistant:
        client = HomeAssistantClient(settings.home_assistant_url or "", settings.home_assistant_token or "")
        states = await client.get_states()
        return {"categories": get_devices()["categories"], "devices": [state_to_device(item) for item in states]}
    return get_devices()


@router.get("/topology")
async def topology() -> dict[str, Any]:
    return get_topology()


@router.get("/metrics")
async def metrics() -> dict[str, Any]:
    return get_metrics()


@router.get("/events/recent")
async def recent_events(limit: int = 12) -> list[dict[str, Any]]:
    return get_recent_events(limit=limit)


@router.get("/automations")
async def automations() -> list[dict[str, Any]]:
    return get_automations()


@router.post("/actions/execute", response_model=ActionResponse)
async def actions(request: ActionRequest) -> dict[str, Any]:
    return execute_action(request.action_id)


@ws_router.websocket("/ws/realtime")
async def realtime(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(get_realtime_payload())
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        return
