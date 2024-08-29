"""
Created On: July 2024
Created By: Sourav Saha
"""
from utils import logger
import os
import logging
from datetime import datetime

from __version__ import __version__

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, APIRouter
from fastapi_redis_cache import FastApiRedisCache, cache


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

# include routes in app
app.include_router(route)
