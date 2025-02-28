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
from routes.protected_route import protected_route

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
description = """
Open Source Uptime Monitor for APIs, Websites, Events etc. with real-time alert. 🚀

## Public Endpoints - /api/v1/external/
* Can be invoked from anywhere without any authentication
* IP level Rate Limit applies

## External Endpoints - /api/v1/external/
* Must be used with **x-api-key** header
* User Level Rate Limit applies

## Internal Endpoints - /api/v1/internal/
* Can NOT be invoked from outside world.
"""
app = FastAPI(
    title=__service__.title(),
    version=__version__,
    lifespan=lifespan,
    description=description,
    docs_url='/api/docs',
    redoc_url='/api/redoc',
    terms_of_service="https://www.finanssure.com/privacy/",
    contact={
        "name": "Finanssure",
        "url": "https://www.finanssure.com/watchtower/",
        "email": "support@finanssure.com",
    },
    license_info={
        "name": "MIT",
        "identifier": "MIT",
    },
)

# include routes in app
app.include_router(internal_route, prefix='/internal/v1')
app.include_router(public_route, tags=['public'], prefix='/api/public/v1')
app.include_router(protected_route, prefix='/api/external/v1')
