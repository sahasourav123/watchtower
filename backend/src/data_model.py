from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel
from enum import Enum

# Monitor Types
class MonitorTypes(str, Enum):
    API = 'api'
    WEBSITE = 'website'
    DOMAIN = 'domain'
    SSL = 'ssl'
    TCP = 'tcp'
    DNS = 'dns'
    DATABASE = 'database'

class MonitorModel(BaseModel, use_enum_values=True):
    monitor_name: Optional[str] = None
    monitor_type: MonitorTypes = None
    monitor_body: Optional[dict] = None
    timeout: Optional[int] = None
    interval: Optional[int] = None
    interval_unit: Optional[Literal['seconds', 'minutes', 'hours', 'days', 'weeks']] = None
    expiry: Optional[datetime] = None
    expectation: Optional[dict] = None
    alerts: Optional[list[int]] = None
    is_active: Optional[bool] = None

class AlertChannelModel(BaseModel):
    channel_name: Optional[str] = None
    channel_type: Literal['email', 'telegram', 'slack', 'webhook'] = None
    recipient: Optional[dict] = None
    is_active: Optional[bool] = None
    remarks: Optional[str] = None
