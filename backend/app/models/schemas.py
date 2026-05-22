from typing import Literal

from pydantic import BaseModel, Field


DeviceCategoryId = Literal[
    "light",
    "sensor",
    "climate",
    "plug",
    "lock",
    "curtain",
    "vacuum",
    "security",
    "unknown",
]

DeviceStatus = Literal["online", "offline", "warning", "unknown"]


class Device(BaseModel):
    id: str
    name: str
    category: DeviceCategoryId
    room: str
    status: DeviceStatus
    state: str
    domain: str
    updated_at: str | None = None
    source: Literal["mock", "home_assistant"] = "mock"


class DeviceCategory(BaseModel):
    id: str
    label: str
    count: int


class ActionRequest(BaseModel):
    action_id: str = Field(..., min_length=1)
    payload: dict | None = None


class ActionResponse(BaseModel):
    success: bool
    action_id: str
    message: str
