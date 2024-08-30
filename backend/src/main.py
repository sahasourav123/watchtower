"""
Created On: July 2024
Created By: Sourav Saha
"""
from utils import logger
import os
import logging
from datetime import datetime
from typing import Literal

from __version__ import __version__

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, APIRouter, Body
from fastapi_redis_cache import FastApiRedisCache, cache

import controller

# Initialize app
__service__ = 'the-towerhouse-backend'
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

# create api monitor
@route.post("/create/monitor")
def create_monitor(monitor_type: Literal["api", "website", "database", "server", "ssl", "mq"], monitor_data=Body(...)):
    monitor_id = controller.create_monitor({'monitor_type': monitor_type,  **monitor_data})
    return {"message": "Monitor created successfully", "monitor_id": monitor_id}

@route.post("/import/monitor")
def create_monitor(monitor_type: Literal["api", "website", "database", "server", "ssl", "mq"]):
    return {"message": "Monitor imported successfully"}

@route.post("/export/monitor")
def create_monitor(monitor_type: Literal["api", "website", "database", "server", "ssl", "mq"]):
    return {"message": "Monitor exported successfully"}

# update monitor
@route.put("/update/monitor/{monitor_id}")
def update_monitor(monitor_id: int):
    return {"message": "Monitor updated successfully"}

# delete monitor
@route.delete("/delete/monitor/{monitor_id}")
def delete_monitor(monitor_id: int):
    return {"message": "Monitor deleted successfully"}

# get monitor(s)
@route.get("/fetch/monitors/{monitor_id}")
def get_monitors(monitor_id: int):
    return {"message": "Monitor fetched successfully"}

# get monitoring history
@route.get("/fetch/history/monitors/{monitor_id}")
def get_monitor_history(monitor_id: int):
    return {"message": "Monitor history fetched successfully"}

# get status page
@route.get("/fetch/statuspage/{statuspage_id}")
def get_statuspage(statuspage_id: int):
    return {"message": "Status page fetched successfully"}

# create status page
@route.post("/create/statuspage")
def create_statuspage():
    return {"message": "Status page created successfully"}

# update status page
@route.put("/update/statuspage/{statuspage_id}")
def update_statuspage(statuspage_id: int):
    return {"message": "Status page updated successfully"}

# delete status page
@route.delete("/delete/statuspage/{statuspage_id}")
def delete_statuspage(statuspage_id: int):
    return {"message": "Status page deleted successfully"}

# create alert group
@route.post("/create/alert")
def create_alert_channel():
    return {"message": "Alert channel created successfully"}

# update alert group
@route.put("/update/alert/{alert_id}")
def update_alert_channel(alert_id: int):
    return {"message": "Alert channel updated successfully"}

# delete alert group
@route.delete("/delete/alert/{alert_id}")
def delete_alert_channel(alert_id: int):
    return {"message": "Alert channel deleted successfully"}

# get alert group
@route.get("/fetch/alert/{alert_id}")
def get_alert_channel(alert_id: int):
    return {"message": "Alert channel fetched successfully"}


# include routes in app
app.include_router(route)
