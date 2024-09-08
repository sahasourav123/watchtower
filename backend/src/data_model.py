from typing import Literal, Optional
from pydantic import BaseModel

class MonitorModel(BaseModel):
    org_id: Optional[int] = None
    monitor_name: Optional[str] = None
    monitor_body: Optional[dict] = None
    timeout: Optional[int] = None
    interval: Optional[int] = None
    expectation: Optional[dict] = None
    alerts: Optional[list[int]] = None
    is_active: Optional[bool] = None
