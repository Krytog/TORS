from raft.state import STATE, LogEntry
from raft.config import MY_ID, CONFIG
from db import crud, log_applier
from db.db import KV_STORE
from common.logging import logger

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from functools import wraps
import concurrent
import requests


READ_TIMEOUT = 0.3

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


@router.get("/localdata/{key}")
async def read_key_local(key):
    applied_index = STATE.log_last_applied
    data = crud.read_key(key)
    if data:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"applied_index": applied_index})
    return JSONResponse(status_code=status.HTTP_200_OK, content={"applied_index": applied_index, "data": data})


@router.get("/data/{key}")
async def read_key(key):
    count = 1  # count ourself
    latest_apply = STATE.log_last_applied
    latest_value = crud.read_key(key)

    def read_key_task(addr, key):
        try:
            response = requests.get(f"http://{addr}/localdata/{key}", timeout=READ_TIMEOUT)
            if response.status_code != 200:
                return None, 0
            index = response.get("applied_inex")
            data = response.get("data", None)
            return data, index
        except Exception as err:
            logger.debug(f"Something went wrong in read_key_task. What: {str(err)}")
        return None, 0

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = set()
        for server_id, server in CONFIG.items():
            if int(server_id) == MY_ID:
                continue
            host, port = server[0], server[1]
            futures.add(executor.submit(read_key_task, f"{host}:31{int(port) % 1000}", key))
        try:
            for future in concurrent.futures.as_completed(futures, timeout=3 * READ_TIMEOUT):
                result = future.result()
                data, index = result[0], result[1]
                if index > latest_apply:
                    latest_apply = index
                    latest_value = data
                if index != 0:
                    count += 1
                if count >= len(CONFIG) // 2 + 1:
                    for unfinished_future in futures:
                        unfinished_future.cancel()
                    break

        except Exception as err:
            logger.error(f"Something went wrong during local read requests. What: {str(err)}")

    if latest_value:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"value": latest_value})
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


@router.patch("/compare_and_swap")
@need_authority
async def cas_key(key, value, old_value):
    index = STATE.append_to_log_safe(
        LogEntry(
            term=STATE.term,
            command="cas",
            key=key,
            value=value,
            old_value=old_value,
        )
    )
    result = await log_applier.wait_for_apply(index)
    if result is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Failed to cas: no such key"})
    if result is False:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": "False", "message": "Value is not changed, old_value != cur_value"})
    return JSONResponse(status_code=status.HTTP_200_OK, content={"success": "True", "message": "Successfully changed value"})


@router.get("/debug/log")
async def debug_log():
    size = len(STATE.log)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"Log size is {size}"})


@router.get("/debug/store")
async def debug_store():
    return JSONResponse(status_code=status.HTTP_200_OK, content=KV_STORE.data)
