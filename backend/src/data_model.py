from typing import Literal, Optional
from pydantic import BaseModel

class MonitorModel(BaseModel):
    org_id: Optional[int] = None
    user_code: Optional[str] = None
    monitor_name: Optional[str] = None
    monitor_type: Literal['api', 'website', 'server'] = None
    monitor_body: Optional[dict] = None
    timeout: Optional[int] = None
    interval: Optional[int] = None
    expectation: Optional[dict] = None
    alerts: Optional[list[int]] = None
    is_active: Optional[bool] = None

class AlertChannelModel(BaseModel):
    channel_name: Optional[str] = None
    channel_type: Literal['email', 'slack', 'webhook'] = None
    recipient: Optional[str] = None
    user_code: Optional[str] = None
    org_id: Optional[int] = None
    is_active: Optional[bool] = None
    remarks: Optional[str] = None
