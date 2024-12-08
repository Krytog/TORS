from raft.state import STATE
from raft.config import MY_ID

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from functools import wraps


router = APIRouter()


def need_authority(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if MY_ID != STATE.leader_id:
            return JSONResponse(status_code=status.HTTP_302_FOUND, content={"leader_id": STATE.leader_id, "message": "For this operation you have to request leader"})
        return await func(*args, **kwargs)
    return wrapper


@router.get("/leader")
async def read_key():
    if STATE.leader_id == 0:
        return JSONResponse(status_code=200, content={"message": "There is not leader now"})
    return JSONResponse(status_code=200, content={"leader_id": STATE.leader_id})


@router.get("/data/{key}")
async def read_key(key):
    print(f"Tried to read key = {key}", flush=True)


@router.post("/create")
@need_authority
async def create_key(key):
    print(f"Tried to create key = {key}", flush=True)


@router.post("/delete")
@need_authority
async def delete_key(key):
    print(f"Tried to delete key = {key}", flush=True)
