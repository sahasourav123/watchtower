"""
Created On: July 2024
Created By: Sourav Saha
"""
from utils.commons import logger
import os
import logging
from datetime import datetime
from typing import Literal

from __version__ import __version__

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, APIRouter
from fastapi.responses import JSONResponse
from fastapi_redis_cache import FastApiRedisCache, cache

import data_model as dm
import scheduler as sch
import controller as ct
import query_engine as qe

# Initialize app
__service__ = 'the-watchtower-backend'
tags_metadata = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    logger.info(f"Connecting to Redis: {REDIS_URL}")
    redis_cache = FastApiRedisCache()
    redis_cache.init(
        host_url=REDIS_URL,
        prefix=f"{__service__}-cache",
        response_header="x-api-cache",
        ignore_arg_types=[Request, Response]
    )
    logging.getLogger('fastapi_redis_cache.client').setLevel(logging.WARNING)
    logger.info(f"Service started: {__service__} | {__version__}")
    yield
    logger.info(f"Service stopped: {__service__} | {__version__}")

# Application setup
app = FastAPI(title=__service__, version=__version__, openapi_tags=tags_metadata, lifespan=lifespan)
route = APIRouter(prefix="/api/v1")
DEFAULT_CACHE_EXPIRE = 60

@app.get("/")
@route.get("/")
async def root():
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {"service": __service__, 'version': __version__, 'server-time': dt}


"""
================================================
MONITORS
================================================
"""
# create api monitor
@route.post("/create/monitor", tags=['monitor'])
def create_monitor(monitor_type: Literal["api", "website", "database", "server", "ssl", "mq"], monitor_data: dm.MonitorModel):
    # insert into database
    monitor_id = qe.insert_monitor({'monitor_type': monitor_type, **monitor_data.model_dump()})
    # schedule monitoring
    sch.create_job(monitor_id, monitor_data.interval)
    return {"message": "Monitor created successfully", "monitor_id": monitor_id}

# update monitor
@route.put("/update/monitor/{monitor_id}", tags=['monitor'])
def update_monitor(monitor_id: int, monitor_data: dm.MonitorModel):
    if monitor_data.interval:
        sch.create_job(monitor_id, monitor_data.interval)
    qe.update_monitor(monitor_id, monitor_data.model_dump(exclude_none=True))
    return {"message": "Monitor updated successfully"}

# delete monitor
@route.delete("/delete/monitor/{monitor_id}", tags=['monitor'])
def delete_monitor(monitor_id: int):
    sch.scheduler.remove_job(f"monitor#{monitor_id}")
    return {"message": "Monitor deleted successfully"}

# get monitor(s)
@route.get("/fetch/monitor", tags=['monitor'])
@cache(expire=30)
def get_monitors(response: Response, org_id: int = None, user_code: str = None):
    df = qe.get_monitors({'org_id': org_id, 'user_code': user_code})
    return {"message": "Monitor fetched successfully", "data": df.to_dict('records')}

# run monitor
@route.get("/run/monitor/{monitor_id}", tags=['monitor'])
def run_monitor(monitor_id: int):
    outcome = ct.run_monitor_by_id(monitor_id)
    return {'is_success': outcome}

# refresh monitor
@route.get("/refresh/monitor", tags=['monitor'])
def refresh_monitor():
    df = qe.get_all_monitors()
    for idx, row in df.iterrows():
        sch.create_job(row['monitor_id'], row['interval'])

    return {"message": "Monitor refreshed successfully"}

# get monitoring history
@route.get("/fetch/history/monitor/{monitor_id}", tags=['monitor'])
def get_monitor_history(monitor_id: int):
    return {"message": "Monitor history fetched successfully"}

# get recent history
@route.get("/fetch/recent/monitor", tags=['monitor'])
def get_recent_monitor_history(org_id: int = None, user_code: str = None, limit: int = 10):
    if not org_id and not user_code:
        return JSONResponse({"message": "Please provide either org_id or user_code"}, status_code=400)
    elif org_id:
        df = qe.fetch_recent_history_by_org(org_id, limit)
    else:
        df = qe.fetch_recent_history_by_user(user_code, limit)

    return {"message": "Recent monitor history fetched successfully", "data": df.to_dict('records')}


@route.post("/import/monitor", tags=['monitor'])
def import_monitor(org_id: int):
    return {"message": "Monitor imported successfully"}

@route.post("/export/monitor", tags=['monitor'])
def export_monitor(org_id: int):
    pass


"""
================================================
STATUS PAGE
================================================
"""
# get status page
@route.get("/fetch/statuspage/{page_id}", tags=['status-page'])
def get_statuspage(page_id: int):
    return {"message": "Status page fetched successfully"}

# create status page
@route.post("/create/statuspage", tags=['status-page'])
def create_statuspage():
    return {"message": "Status page created successfully"}

# update status page
@route.put("/update/statuspage/{page_id}", tags=['status-page'])
def update_statuspage(page_id: int):
    return {"message": "Status page updated successfully"}

# delete status page
@route.delete("/delete/statuspage/{page_id}", tags=['status-page'])
def delete_statuspage(page_id: int):
    return {"message": "Status page deleted successfully"}


"""
================================================
ALERTS
================================================
"""
# fetch alert group
@route.get("/fetch/channel", tags=['alert'])
def fetch_alert_channel(user_code: str):
    channel_df = qe.get_alert_channel(user_code)
    return {"message": "Alert channel updated successfully", "data": channel_df.to_dict('records')}

# create alert group
@route.post("/create/channel", tags=['alert'])
def create_alert_channel(data: dm.AlertChannelModel):
    channel_id = qe.insert_alert_channel(data.model_dump())
    return {'channel_id': channel_id, "message": "Alert channel created successfully"}

# update alert group
@route.put("/update/channel/{channel}", tags=['alert'])
def update_alert_channel(channel_id: int):
    return {"message": "Alert channel updated successfully"}

# delete alert group
@route.delete("/delete/channel/{alert_id}", tags=['alert'])
def delete_alert_channel(channel_id: int):
    return {"message": "Alert channel deleted successfully"}


# include routes in app
app.include_router(route)
