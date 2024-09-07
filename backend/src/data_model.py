from typing import Literal, Optional
from pydantic import BaseModel, Extra, PositiveInt, Field

class MonitorModel(BaseModel):
    org_id: PositiveInt | None = None
    # monitor_type: Literal["api", "website", "database", "server", "ssl", "mq"]
    monitor_name: str | None = None
    monitor_body: dict | None = None
    timeout: int | None = None
    interval: int | None = None
    expectation: dict | None = None
    alerts: list[int] | None = None
    is_active: bool | None = None
