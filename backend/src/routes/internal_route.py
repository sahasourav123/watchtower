"""
this route contains those endpoints which are only used by internal microservices
Created On: Feb 2025
Created By: Sourav Saha
"""
from fastapi import Response, APIRouter
import secrets

import os
import json
import redis
import controller as ct
import data_model as dm
import query_engine as qe

from fastapi_redis_cache import cache

DEFAULT_CACHE_EXPIRE = 60
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
redis_conn = redis.Redis.from_url(REDIS_URL)
internal_route = APIRouter()

# Generate API token for a user_code. This endpoint is NOT exposed. Only invoked from the frontend after user login
@internal_route.get("/generate/token")
def generate_token(user_code: str):
    token = secrets.token_hex(32)
    redis_conn.set(token, user_code)
    return {"token": token}


"""
================================================
MONITORS
================================================
"""
# create api monitor
@internal_route.post("/create/monitor")
def create_monitor(user_code: str, monitor_type: dm.MonitorTypes, monitor_data: dm.MonitorModel):
    monitor_id = ct.create_monitor(user_code, monitor_type.value, monitor_data)
    return {"status": "success", "monitor_id": monitor_id}

@internal_route.put("/update/monitor/{monitor_id}")
def update_monitor(user_code: str, monitor_id: int, monitor_data: dm.MonitorModel):
    result = ct.update_monitor(user_code, monitor_id, monitor_data)
    return {"status": "success"}

# delete monitor
@internal_route.delete("/delete/monitor/{monitor_id}")
def delete_monitor(user_code: str, monitor_id: int):
    result = ct.delete_monitor(user_code, monitor_id)
    return {"status": "success"}

# get monitor(s)
@internal_route.get("/fetch/monitor")
@cache(expire=DEFAULT_CACHE_EXPIRE)
def get_monitors(response: Response, user_code: str = None):
    df = qe.get_monitors({'user_code': user_code})
    return {"status": "success", "data": json.loads(df.to_json(orient='records'))}

# run monitor
@internal_route.get("/run/monitor/{monitor_id}")
def run_monitor(monitor_id: int, user_code: str):
    outcome = ct.run_monitor_by_id(monitor_id)
    return {'is_success': outcome}


"""
================================================
STATS
================================================
"""
# monitor stats
@internal_route.get("/stats")
@cache(expire=DEFAULT_CACHE_EXPIRE)
def get_monitor_stats(response: Response, user_code: str):
    df = qe.monitor_stats(user_code)
    return {"status": "success", "data": df.to_dict('records')}

# get recent history
@internal_route.get("/fetch/history")
def get_recent_monitor_history(user_code: str, limit: int = 10):
    df = qe.fetch_recent_history_by_user({'user_code': user_code}, limit)
    return {"status": "success", "data": df.to_dict('records')}


# get monitoring history
@internal_route.get("/fetch/uptime", tags=['uptime'])
def get_monitor_history(user_code: str, day_limit: int = 90):
    df = qe.daily_uptime_history({'user_code': user_code}, day_limit)
    return {"status": "success", 'count': df.shape[0], "data": df.to_dict('records')}


"""
================================================
JOBS
================================================
"""
# refresh monitor
@internal_route.get("/refresh/monitor")
def refresh_monitor():
    count = ct.refresh_monitor()
    return {"status": "success", "count": count}


"""
================================================
TODO: ALERTS
================================================
"""
# fetch alert group
@internal_route.get("/fetch/channel", tags=['alert'])
def fetch_alert_channel(user_code: str):
    channel_df = qe.get_alert_channel(user_code)
    return {"message": "Alert channel updated successfully", "data": channel_df.to_dict('records')}

# create alert group
@internal_route.post("/create/channel", tags=['alert'])
def create_alert_channel(data: dm.AlertChannelModel):
    channel_id = qe.insert_alert_channel(data.model_dump())
    return {'channel_id': channel_id, "message": "Alert channel created successfully"}

# update alert group
@internal_route.put("/update/channel/{channel}", tags=['alert'])
def update_alert_channel(channel_id: int):
    return {"message": "Alert channel updated successfully"}

# delete alert group
@internal_route.delete("/delete/channel/{alert_id}", tags=['alert'])
def delete_alert_channel(channel_id: int):
    return {"message": "Alert channel deleted successfully"}

