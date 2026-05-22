import asyncio
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import get_settings
from app.models.schemas import ActionRequest, ActionResponse
from app.services.home_assistant import HomeAssistantClient, build_device_categories, states_to_devices
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
    settings = get_settings()
    if settings.use_home_assistant:
        client = HomeAssistantClient(settings.home_assistant_url or "", settings.home_assistant_token or "")
        device_items = states_to_devices(await client.get_states())
        total = len(device_items)
        online = sum(1 for device in device_items if device.status == "online")
        offline = sum(1 for device in device_items if device.status == "offline")
        warning = sum(1 for device in device_items if device.status == "warning")
        health = round(((online / total) * 100) - warning * 3, 1) if total else 0
        return {
            "total_devices": total,
            "online_devices": online,
            "offline_devices": offline,
            "today_events": 0,
            "home_health": max(0, min(100, health)),
            "updated_at": None,
        }
    return get_overview()


@router.get("/devices")
async def devices() -> dict[str, Any]:
    settings = get_settings()
    if settings.use_home_assistant:
        client = HomeAssistantClient(settings.home_assistant_url or "", settings.home_assistant_token or "")
        states = await client.get_states()
        device_items = states_to_devices(states)
        return {
            "categories": [category.model_dump() for category in build_device_categories(device_items)],
            "devices": [device.model_dump() for device in device_items],
        }
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
