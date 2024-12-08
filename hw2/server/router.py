from raft.state import STATE, LogEntry
from raft.config import MY_ID, CONFIG
from db import crud
from db import log_applier

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from functools import wraps


router = APIRouter()


def get_leader_address(leader_id):
    str_id = str(leader_id)
    return f"localhost:31{int(CONFIG[str_id][1]) % 1000}"


def need_authority(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if MY_ID != STATE.leader_id:
            return JSONResponse(status_code=status.HTTP_302_FOUND, content={"leader_id": STATE.leader_id, "address": get_leader_address(STATE.leader_id), "message": "For this operation you have to request leader"})
        return await func(*args, **kwargs)
    return wrapper


@router.get("/leader")
async def get_leader():
    if STATE.leader_id == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "There is not leader now"})
    return JSONResponse(status_code=status.HTTP_200_OK, content={"leader_id": STATE.leader_id, "address": get_leader_address(STATE.leader_id)})


@router.get("/data/{key}")
async def read_key(key):
    value = crud.read_key(key)
    if value:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"value": value})
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "No such key exists"})


@router.post("/create")
@need_authority
async def create_key(key, value):
    index = STATE.append_to_log_safe(
        LogEntry(
            term=STATE.term,
            command="create",
            key=key,
            value=value
        )
    )
    result = await log_applier.wait_for_apply(index)
    if result is False:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": "Failed to create: such a key already exists"})
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Successfully created"})


@router.post("/delete")
@need_authority
async def delete_key(key):
    index = STATE.append_to_log_safe(
        LogEntry(
            term=STATE.term,
            command="delete",
            key=key,
            value=None
        )
    )
    result = await log_applier.wait_for_apply(index)
    if result is False:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Failed to delete: no such key"})
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Successfully deleted"})


@router.put("/update")
@need_authority
async def update_key(key, value):
    index = STATE.append_to_log_safe(
        LogEntry(
            term=STATE.term,
            command="update",
            key=key,
            value=value
        )
    )
    result = await log_applier.wait_for_apply(index)
    if result is False:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Failed to update: no such key"})
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Successfully updated"})
