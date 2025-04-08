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
    REDIS_URL = os.getenv('REDIS_URL')
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
### API Architecture Overview

The system utilizes a tiered API structure to manage access control, security, and usage patterns effectively:

1.  **`/api/public/v1/` - Public Endpoints**
    * **Description:** Provides read-only or general status information accessible without credentials.
    * **Authentication:** Anonymous. No API keys or logins are needed.
    * **Security Context:** Lowest privilege; designed for safe public exposure.
    * **Constraints:** Subject to rate limiting based on the client's source IP address to ensure fair use and mitigate DoS risks.
    * **Typical Use:** Embedding status updates on public websites, simple health checks.

2.  **`/api/external/v1/` - Authenticated External Endpoints**
    * **Description:** Enables authenticated interactions for managing resources, retrieving user-specific data, or triggering actions.
    * **Authentication:** Requires a valid API Key passed in the standard `x-api-key` request header.
    * **Security Context:** User/Application-level privileges based on the provided key.
    * **Constraints:** Rate limits are enforced per API key, allowing different tiers of usage based on the associated account or application.
    * **Typical Use:** Third-party integrations, custom monitoring clients, automation scripts.

3.  **`/internal/v1/` - Internal Service Endpoints**
    * **Description:** Core backend APIs used for internal operations and communication between services within the system.
    * **Authentication:** Not designed for direct external authentication; access is typically controlled at the network level (e.g., firewall rules, private VPC, localhost binding).
    * **Security Context:** Assumes a trusted internal environment within a self-hosted deployment.
    * **Constraints:** May have internal performance controls but generally bypasses external rate-limiting logic.
    * **Typical Use:** Essential for the functioning of self-hosted instances (e.g., communication between scheduler, checker, and notification services). **Do not attempt to call these from outside the deployment.**
"""
app = FastAPI(
    title=__service__.title(),
    version=__version__,
    lifespan=lifespan,
    description=description,
    docs_url='/api/docs',
    redoc_url='/api/redoc',
    openapi_url='/api/openapi.json',
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
