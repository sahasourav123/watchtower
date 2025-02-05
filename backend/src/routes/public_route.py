"""
This file contains the routes which are used by anyone, without any authentication.
Created On: Feb 2025
Created By: Sourav Saha
"""
import json
from datetime import datetime
from fastapi import Response, APIRouter, Body

import controller as ct
import data_model as dm
import query_engine as qe
from fastapi_redis_cache import cache

from __version__ import __service__, __version__

public_route = APIRouter()
DEFAULT_CACHE_EXPIRE = 60

@public_route.get("/")
async def root():
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {"service": __service__, 'version': __version__, 'server-time': dt}

# check status
@public_route.get("/check")
def check_status(monitor_type: dm.MonitorTypes, monitor_body: dict = Body(...)):
    result = ct.run_monitor(monitor_type, monitor_body)
    return result

@public_route.get("/stats/global")
@cache(expire=DEFAULT_CACHE_EXPIRE)
def get_monitor_stats(response: Response):
    df = qe.monitor_stats()
    return {"status": "success", "data": df.to_dict('records')}

@public_route.get("/fetch/monitor")
@cache(expire=DEFAULT_CACHE_EXPIRE)
def get_monitors(response: Response, org_id: int = None, user_code: str = None):
    df = qe.get_monitors({'tags': '{guest, public}'})
    return {"status": "success", "data": json.loads(df.to_json(orient='records'))}

# get recent history
@public_route.get("/fetch/history")
def get_recent_monitor_history(limit: int = 10):
    df = qe.fetch_recent_history_by_user({'tags': '{guest, public}'}, limit)
    return {"status": "success", "data": df.to_dict('records')}

@public_route.get("/fetch/uptime", tags=['uptime'])
@cache(expire=DEFAULT_CACHE_EXPIRE)
def get_monitor_history(response: Response, user_code: str, day_limit: int = 90):
    df = qe.daily_uptime_history({'tags': '{guest, public}'}, day_limit)
    return {"status": "success", 'count': df.shape[0], "data": df.to_dict('records')}

