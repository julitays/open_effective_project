from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BarrierMitigationPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    barrier_id: UUID
    action_type: str
    action_text: str
    owner_role: str
    due_period: str | None
    status: str
    confirmation_status: str | None
    check_method: str | None
    expected_effect: str | None
    actual_effect: str | None
    effect_status: str | None
    created_at: datetime
    updated_at: datetime
