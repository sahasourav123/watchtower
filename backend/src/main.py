"""
Created On: July 2024
Created By: Sourav Saha
"""
from commons import logger
import os
import logging
from datetime import datetime
from typing import Literal

from __version__ import __version__

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, APIRouter, Body
from fastapi_redis_cache import FastApiRedisCache, cache

import data_model as dm
import scheduler as sch
import controller as ct

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
    monitor_id = ct.insert_monitor({'monitor_type': monitor_type, **monitor_data})
    # schedule monitoring
    sch.create_job(monitor_id, monitor_data.interval)
    return {"message": "Monitor created successfully", "monitor_id": monitor_id}

# update monitor
@route.put("/update/monitor/{monitor_id}", tags=['monitor'])
def update_monitor(monitor_id: int, monitor_data: dm.MonitorModel):
    if monitor_data.interval:
        sch.create_job(monitor_id, monitor_data.interval)
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
    df = ct.get_monitors({'org_id': org_id, 'user_code': user_code})
    return {"message": "Monitor fetched successfully", "data": df.to_dict('records')}

# run monitor
@route.get("/run/monitor/{monitor_id}", tags=['monitor'])
def run_monitor(monitor_id: int):
    outcome = ct.run_monitor_by_id(monitor_id)
    return {'is_success': outcome}

# refresh monitor
@route.get("/refresh/monitor", tags=['monitor'])
def refresh_monitor():
    df = ct.get_all_monitors()
    for idx, row in df.iterrows():
        sch.create_job(row['monitor_id'], row['interval'])

    return {"message": "Monitor refreshed successfully"}

# get monitoring history
@route.get("/fetch/history/monitor/{monitor_id}", tags=['monitor'])
def get_monitor_history(monitor_id: int):
    return {"message": "Monitor history fetched successfully"}

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
# create alert group
@route.post("/create/alert", tags=['alert'])
def create_alert_channel():
    return {"message": "Alert channel created successfully"}

# update alert group
@route.put("/update/alert/{alert_id}", tags=['alert'])
def update_alert_channel(alert_id: int):
    return {"message": "Alert channel updated successfully"}

# delete alert group
@route.delete("/delete/alert/{alert_id}", tags=['alert'])
def delete_alert_channel(alert_id: int):
    return {"message": "Alert channel deleted successfully"}

# get alert group
@route.get("/fetch/alert/{alert_id}", tags=['alert'])
def get_alert_channel(alert_id: int):
    return {"message": "Alert channel fetched successfully"}


# include routes in app
app.include_router(route)
