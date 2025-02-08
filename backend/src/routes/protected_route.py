"""
this route contains those endpoints which are used by any authenticated user
Created On: Feb 2025
Created By: Sourav Saha
"""
from fastapi import Request, Response, APIRouter, Body, Depends, Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

import controller as ct
import data_model as dm
from utils.db_util import RedisManager

rd = RedisManager()


async def validate_token(request: Request, token: str = Security(APIKeyHeader(name='x-api-key', auto_error=False))) -> str:
    user_code = rd.get(token) if token else None

    if not user_code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Expired API Key",
        )

    request.state.user_code = user_code
    return user_code

protected_route = APIRouter(dependencies=[Depends(validate_token)])

@protected_route.post("/create/monitor", tags=['monitor'])
def create_monitor(request: Request, monitor_type: dm.MonitorTypes, monitor_data: dm.MonitorModel):
    user_code = request.state.user_code
    monitor_id = ct.create_monitor(request.state.user_code, monitor_type.value, monitor_data)
    return {"status": "success", "monitor_id": monitor_id}

# update monitor
@protected_route.put("/update/monitor/{monitor_id}", tags=['monitor'])
def update_monitor(request: Request, monitor_id: int, monitor_data: dm.MonitorModel):
    user_code = request.state.user_code
    result = ct.update_monitor(request.state.user_code, monitor_id, monitor_data)
    return {"status": "success"}

# delete monitor
@protected_route.delete("/delete/monitor/{monitor_id}", tags=['monitor'])
def delete_monitor(request: Request, monitor_id: int):
    user_code = request.state.user_code
    result = ct.delete_monitor(request.state.user_code, monitor_id)
    return {"status": "success"}
