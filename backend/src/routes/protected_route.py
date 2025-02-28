"""
this route contains those endpoints which are used by any authenticated user
Created On: Feb 2025
Created By: Sourav Saha
"""
import json
from fastapi import Request, Response, APIRouter, Depends, Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

import data_model as dm
from utils import commons
from utils.db_util import RedisManager
from routes import internal_route

rd = RedisManager()
config = commons.load_config()


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

async def assert_permission(request: Request):
    if request.state.permission != 'read-write':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Read-Write Permission Required.",
        )


protected_route = APIRouter(dependencies=[Depends(validate_token)])

@protected_route.post("/create/monitor", tags=['monitor'], dependencies=[Depends(assert_permission)])
async def create_monitor(request: Request, monitor_type: dm.MonitorTypes, monitor_data: dm.MonitorModel):
    internal_response = await internal_route.create_monitor(request.state.user_code, monitor_type.value, monitor_data)
    return json.loads(internal_response.body.decode("utf-8"))

# update monitor
@protected_route.put("/update/monitor/{monitor_id}", tags=['monitor'])
async def update_monitor(request: Request, monitor_id: int, monitor_data: dm.MonitorModel):
    internal_response = await internal_route.update_monitor(request.state.user_code, monitor_id, monitor_data)
    return json.loads(internal_response.body.decode("utf-8"))

# delete monitor
@protected_route.delete("/delete/monitor/{monitor_id}", tags=['monitor'], dependencies=[Depends(assert_permission)])
async def delete_monitor(request: Request, monitor_id: int):
    internal_response = await internal_route.delete_monitor(request.state.user_code, monitor_id=monitor_id)
    return json.loads(internal_response.body.decode("utf-8"))

@protected_route.get("/fetch/monitor", tags=['monitor'])
async def fetch_monitor(request: Request, response: Response):
    internal_response = await internal_route.get_monitors(response, user_code=request.state.user_code)
    return json.loads(internal_response.body.decode("utf-8"))
