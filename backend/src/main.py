"""
Created On: July 2024
Modified On: Feb 2025
Created By: Sourav Saha
"""
from utils.commons import logger
import os
import logging

from __version__ import __service__, __version__

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi_redis_cache import FastApiRedisCache

from routes.public_route import public_route
from routes.internal_route import internal_route

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
app = FastAPI(
    title=__service__.title(),
    version=__version__,
    lifespan=lifespan,
    # openapi_tags=tags_metadata,
    # redoc_url=f"{BASE_ROUTE}/redoc",
    # docs_url=f"{BASE_ROUTE}/docs",
)

# include routes in app
app.include_router(public_route, tags=['public'], prefix='/public/v1')
app.include_router(internal_route, tags=['internal'], prefix='/internal/v1')
