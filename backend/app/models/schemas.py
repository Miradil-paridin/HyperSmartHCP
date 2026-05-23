from typing import Literal

from pydantic import BaseModel, Field, model_validator


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
    controllable: bool = False
    updated_at: str | None = None
    source: Literal["mock", "home_assistant"] = "mock"


class DeviceCategory(BaseModel):
    id: str
    label: str
    count: int


class ActionRequest(BaseModel):
    action_id: str | None = Field(default=None, min_length=1)
    entity_id: str | None = Field(default=None, min_length=1)
    service: str | None = Field(default=None, min_length=1)
    service_data: dict | None = None
    payload: dict | None = None

    @model_validator(mode="after")
    def validate_action_shape(self) -> "ActionRequest":
        if self.action_id:
            return self
        if self.entity_id and self.service:
            return self
        raise ValueError("action_id or entity_id + service is required")


class ActionResponse(BaseModel):
    success: bool
    action_id: str | None = None
    entity_id: str | None = None
    service: str | None = None
    message: str
