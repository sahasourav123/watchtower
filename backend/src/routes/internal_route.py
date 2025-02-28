"""
this route contains those endpoints which are only used by internal microservices
Created On: Feb 2025
Created By: Sourav Saha
"""
from fastapi import Response, APIRouter, HTTPException, status
import secrets

import json
import controller as ct
import data_model as dm
import query_engine as qe
from utils import commons
from typing import Literal

from fastapi_redis_cache import cache
from utils.db_util import RedisManager

DEFAULT_CACHE_EXPIRE = 60
internal_route = APIRouter()

"""
================================================
API TOKEN
================================================
"""
rd = RedisManager()

# Generate API token for a user_code. This endpoint is NOT exposed. Only invoked from the frontend after user login
@internal_route.post("/create/token", tags=['token'])
def create_token(user_code: str, permission: Literal['read-only', 'read-write'], name: str = None, expiry_days: int = 30):
    token = secrets.token_hex(32)
    rd.set(f"{user_code}:{token}", {'permission': permission, 'name': name}, ttl=expiry_days * 86400)
    return {"status": "success", "action": "create", "token": token}

@internal_route.delete("/delete/token", tags=['token'])
def delete_token(user_code: str, token: str):
    res = rd.delete(f"{user_code}:{token}")
    if res:
        return {"status": "success", "action": "delete", "token": token}
    else:
        return {"status": "failed", "error": "Invalid token or user_code"}

@internal_route.get("/fetch/token", tags=['token'])
def fetch_token(user_code: str):
    keys = rd.search_keys(f"{user_code}:*")
    data = [{'token': key.split(':')[-1], **rd.get(key, expected_type=dict)} for key in keys]
    return {"status": "success", "data": data}


"""
================================================
MONITORS
================================================
"""
# create api monitor
@internal_route.post("/create/monitor", tags=['monitor'])
def create_monitor(user_code: str, monitor_type: dm.MonitorTypes, monitor_data: dm.MonitorModel):
    monitor_id, _hash = ct.create_monitor(user_code, monitor_type.value, monitor_data)
    return {"status": "success", "monitor_id": monitor_id, "monitor_hash": _hash}

@internal_route.put("/update/monitor/{monitor_id}", tags=['monitor'])
def update_monitor(user_code: str, monitor_id: int, monitor_data: dm.MonitorModel):
    result = ct.update_monitor(user_code, monitor_id, monitor_data)
    if not result:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"monitor #{monitor_id} not found")

    return {"status": "success"}

# delete monitor
@internal_route.delete("/delete/monitor/{monitor_id}", tags=['monitor'])
def delete_monitor(user_code: str, monitor_id: int):
    result = ct.delete_monitor(user_code, monitor_id)
    if not result:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"monitor #{monitor_id} not found")

    return {"status": "success"}

# get monitor(s)
@internal_route.get("/fetch/monitor", tags=['monitor'])
@cache(expire=DEFAULT_CACHE_EXPIRE)
def get_monitors(response: Response, user_code: str = None):
    df = qe.get_monitors({'user_code': user_code})
    return {"status": "success", "data": json.loads(df.to_json(orient='records'))}

# run monitor
@internal_route.get("/run/monitor/{monitor_id}", tags=['monitor'])
def run_monitor(monitor_id: int, user_code: str):
    result = ct.run_monitor_by_id(monitor_id)
    return result if isinstance(result, dict) else {'monitor_id': monitor_id, 'is_success': result}


"""
================================================
STATS
================================================
"""
# monitor stats
@internal_route.get("/stats/monitor", tags=['stats'])
@cache(expire=DEFAULT_CACHE_EXPIRE)
def get_monitor_stats(response: Response, user_code: str):
    df = qe.monitor_stats(user_code)
    return {"status": "success", "data": df.to_dict('records')}

@internal_route.get("/stats/response/{scope}", tags=['stats'])
@cache(expire=DEFAULT_CACHE_EXPIRE)
def get_response_stats(response: Response, scope: Literal['aggregated', 'daily'], user_code: str):
    if scope == 'aggregated':
        df = qe.aggregated_response_stats({'user_code': user_code})
    else:
        df = qe.daily_response_stats({'user_code': user_code})

    return {"status": "success", "data": df.to_dict('records')}

# get recent history
@internal_route.get("/fetch/history", tags=['stats'])
def get_recent_monitor_history(user_code: str, limit: int = 10):
    df = qe.fetch_recent_history_by_user({'user_code': user_code}, limit)
    return {"status": "success", "data": df.to_dict('records')}


# get monitoring history
@internal_route.get("/fetch/uptime", tags=['stats'])
def get_monitor_history(user_code: str, day_limit: int = 90):
    df = qe.daily_uptime_history({'user_code': user_code}, day_limit)
    return {"status": "success", 'count': df.shape[0], "data": df.to_dict('records')}


"""
================================================
OTHER
================================================
"""
# refresh monitor
@internal_route.get("/refresh/monitor", tags=['other'])
def refresh_monitor():
    count = ct.refresh_monitor()
    return {"status": "success", "count": count}

# retrieve monitor hash
@internal_route.get("/compute/hash", tags=['other'])
def compute_monitor_hash(monitor_id: int):
    _hash = commons.compute_hash(monitor_id)
    return {"status": "success", "monitor_id": monitor_id, "hash": _hash}


"""
================================================
ALERT CHANNELS
================================================
"""
# fetch alert group
@internal_route.get("/fetch/channel", tags=['alert'])
def fetch_alert_channel(user_code: str):
    channel_df = qe.get_alert_channel({'user_code': user_code})
    return {"status": "success", "data": channel_df.to_dict('records')}

# create alert group
@internal_route.post("/create/channel", tags=['alert'])
def create_alert_channel(user_code: str, alert_data: dm.AlertChannelModel):
    channel_id = ct.create_alert_channel(user_code, alert_data)
    return {"status": "success", 'channel_id': channel_id}

# delete alert group
@internal_route.delete("/delete/channel/{channel_id}", tags=['alert'])
def delete_alert_channel(channel_id: int):
    qe.delete_alert_channel(channel_id)
    return {"status": "success", 'channel_id': channel_id}
