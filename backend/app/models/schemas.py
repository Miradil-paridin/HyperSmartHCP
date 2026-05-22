from pydantic import BaseModel, Field


class ActionRequest(BaseModel):
    action_id: str = Field(..., min_length=1)
    payload: dict | None = None


class ActionResponse(BaseModel):
    success: bool
    action_id: str
    message: str
