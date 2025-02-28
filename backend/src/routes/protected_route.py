"""
this route contains those endpoints which are used by any authenticated user
Created On: Feb 2025
Created By: Sourav Saha
"""
from fastapi import Request, Response, APIRouter, Body, Depends, Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import RedirectResponse

import controller as ct
import data_model as dm
from utils import commons
from utils.db_util import RedisManager

rd = RedisManager()
config = commons.load_config()
INTERNAL_ROUTE = "/internal/v1"


async def validate_token(request: Request, token: str = Security(APIKeyHeader(name='x-api-key', auto_error=False))) -> str:
    # api token should exist
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key Required",
        )

    # api token should be valid
    keys = rd.search_keys(f"*:{token}")
    if not keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Expired API Key",
        )

    # rate-limit check
    user_code = keys[0].split(":")[0]
    _counter = rd.expiring_counter(user_code, ttl=config['rate-limit']['time-window-in-seconds'])
    if _counter > config['rate-limit']['max-request-count']:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate Limit Exceeded",
        )

    request.state.user_code = user_code
    request.state.permission = rd.get(keys[0], expected_type=dict)['permission']
    return user_code

def assert_permission(request: Request, required_permission: str):
    if request.state.permission != required_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{required_permission} Permission Required.",
        )


protected_route = APIRouter(dependencies=[Depends(validate_token)])

@protected_route.post("/create/monitor", tags=['monitor'])
def create_monitor(request: Request, monitor_type: dm.MonitorTypes, monitor_data: dm.MonitorModel):
    assert_permission(request, 'read-write')
    monitor_id, _hash = ct.create_monitor(request.state.user_code, monitor_type.value, monitor_data)
    return {"status": "success", "monitor_id": monitor_id, "monitor_hash": _hash}

# update monitor
@protected_route.put("/update/monitor/{monitor_id}", tags=['monitor'])
def update_monitor(request: Request, monitor_id: int, monitor_data: dm.MonitorModel):
    assert_permission(request, 'read-write')
    result = ct.update_monitor(request.state.user_code, monitor_id, monitor_data)
    if not result:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"monitor #{monitor_id} not found")

    return {"status": "success"}

# delete monitor
@protected_route.delete("/delete/monitor/{monitor_id}", tags=['monitor'])
def delete_monitor(request: Request, monitor_id: int):
    assert_permission(request, 'read-write')
    return RedirectResponse(url=f"{INTERNAL_ROUTE}/delete/monitor/{monitor_id}?user_code={request.state.user_code}")

@protected_route.get("/fetch/monitor", tags=['monitor'])
def fetch_monitor(request: Request):
    return RedirectResponse(url=f"{INTERNAL_ROUTE}/fetch/monitor?user_code={request.state.user_code}")
